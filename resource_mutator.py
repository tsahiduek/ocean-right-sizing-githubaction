#!/usr/bin/env python3
import requests
from requests.exceptions import *
import yaml
import os
import logging
import argparse

SPOT_API_HOST = "https://api.spotinst.io"
SPOT_RIGHT_SIZING_PATH = "ocean/aws/k8s/cluster/{SPOT_OCEAN_ID}/rightSizing/resourceSuggestion?namespace={NAMESPACE}&accountId={SPOT_ACCOUNT}"
SPOT_OCEAN_ID = "SPOT_OCEAN_ID"
SPOT_OCEAN_CONTROLLER = "SPOT_OCEAN_CONTROLLER"
SPOT_TOKEN = "SPOT_TOKEN"
SPOT_ACCOUNT = "SPOT_ACCOUNT"

DEFAULT_CPU = "200mi"
DEFAULT_MEM = "512Mi"

logging.basicConfig(format=(
    '%(asctime)s %(name)-12s %(funcName)-8s %(message)s'))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_spot_from_env():
    spot_data = {}
    spot_data[SPOT_OCEAN_ID] = os.getenv(SPOT_OCEAN_ID)
    spot_data[SPOT_OCEAN_CONTROLLER] = os.getenv(SPOT_OCEAN_CONTROLLER)
    spot_data[SPOT_TOKEN] = os.getenv(SPOT_TOKEN)
    spot_data[SPOT_ACCOUNT] = os.getenv(SPOT_ACCOUNT)
    return spot_data


def modify_deployment_rs_suggestions(deployment):
    deployment_name = deployment["metadata"]["name"]
    namespace = deployment["metadata"]["namespace"]

    rs_sugg = dict()
    spot_data = load_spot_from_env()

    auth_bearer = "Bearer {SPOT_TOKEN}".format(
        SPOT_TOKEN=spot_data[SPOT_TOKEN])
    headers = {"Content-Type": "application/json"}
    headers.update({"Authorization": auth_bearer})
    with requests.Session() as session:
        url = "/".join([SPOT_API_HOST, SPOT_RIGHT_SIZING_PATH.format(
            SPOT_OCEAN_ID=spot_data[SPOT_OCEAN_ID], NAMESPACE=namespace, SPOT_ACCOUNT=spot_data[SPOT_ACCOUNT])])
        logger.info("url={}".format(url))
        try:
            response = session.get(url=url, headers=headers)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err}')
            return deployment
        except Exception as err:
            logger.error(f'Other error occurred: {err}')
            return deployment
        else:
            logger.info("Request to Ocean API completed with code {}".format(
                response.status_code))

        rs_suggestions = response.json()["response"]["items"]

        for sugg in rs_suggestions:
            if deployment_name == sugg["deploymentName"]:
                rs_sugg = sugg
                break
        suggested_cpu = ""
        suggested_memory = ""
        if rs_sugg["suggestedCPU"] != None:
            suggested_cpu = str(rs_sugg["suggestedCPU"]) + "mi"

        if rs_sugg["suggestedMemory"] != None:
            suggested_memory = str(rs_sugg["suggestedMemory"]) + "Mi"

        for container in deployment["spec"]["template"]["spec"]["containers"]:
            if container.get("resources").get("requests"):
                if suggested_cpu:
                    container["resources"]["requests"]["cpu"] = suggested_cpu
                if suggested_memory:
                    container["resources"]["requests"]["memory"] = suggested_memory
            else:
                container["resources"]["requests"] = dict()

                if container.get("resources").get("limits"):
                    if suggested_cpu:
                        container["resources"]["requests"]["cpu"] = suggested_cpu
                    else:
                        if container.get("resources").get("limits").get("cpu"):
                            container["resources"]["requests"]["cpu"] = container.get(
                                "resources").get("limits").get("cpu")
                        else:
                            container["resources"]["requests"]["cpu"] = DEFAULT_CPU
                    if suggested_memory:
                        container["resources"]["requests"]["memory"] = suggested_memory
                    else:
                        if container.get("resources").get("limits").get("memory"):
                            container["resources"]["requests"]["memory"] = container.get(
                                "resources").get("limits").get("memory")
                        else:
                            container["resources"]["requests"]["memory"] = DEFAULT_MEM

    return deployment


def main(deployment_path):
    directory = deployment_path.split("/")
    yaml_filename = directory[-1]
    directory[-2] = directory[-2] + "-out"
    out_directory = "/".join(directory[:-1])
    os.makedirs(name=out_directory, exist_ok=True)

    out_file = out_directory + "/" + yaml_filename
    with open(deployment_path) as f:

        deployment = yaml.load(f, Loader=yaml.FullLoader)
        mutated_deployment = modify_deployment_rs_suggestions(
            deployment=deployment)
    # write the mutated yaml
    logger.debug(mutated_deployment)
    with open(out_file, "w") as out:
        logger.info("Writing Mutated Deployment")
        logger.info(mutated_deployment)
        yaml.dump(mutated_deployment, out)


if __name__ == "__main__":
    # print(os.path.dirname(os.path.realpath(__file__)))
    # print(os.listdir('.'))
    if os.getenv("DEBUG"):
        logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description='Right Sizing Yaml mutation')
    parser.add_argument('--k8s-yamls', action="store", dest="k8s_yamls", default="K8s/deployment.yaml",
                        help='K8s yaml directory to process')
    args = parser.parse_args()
    k8s_yamls = args.k8s_yamls.split("\n")

    for k8s_yaml in k8s_yamls:
        main(k8s_yaml)
