# Ocean Right Sizing Github Action

[WIP]

Ocean Right Sizing Github Action, uses Spot Ocean [Right Sizing Recmomendations](https://api.spotinst.com/ocean/concepts/ocean-cloud/right-sizing/)

## Usage

In order to use this action, you'll need the following:

- [Spot Account](https://api.spotinst.com/connect-your-cloud-provider-account/) & [Ocean Cluster](https://api.spotinst.com/ocean/tutorials/ocean-for-aws/import-an-eks-based-ocean-cluster/)
- Creating these [Github Secrets](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets) in your repository:
  - SPOT_TOKEN - The Spot token to interact with the Spot API
  - SPOT_ACCOUNT - The Spot Account number in which the Ocean number exists in.
  - SPOT_OCEAN_ID - The Ocean ID of the Ocean cluster
  - SPOT_OCEAN_CONTROLLER - The Cluster Identifier (spotinst.cluster-identifier from the spotinst-kubernetes-cluster-controller-config ConfigMap in your cluster)

This action writes the mutated deployment file to a new directory with the suffix "-OUT" so you'll be able to apply this mutated deployment/s

This is an example of use in this action

````yaml
on: [push]

jobs:
  ocean_right_sizing_deployment_mutation:
    runs-on: ubuntu-latest
    name: Mutate K8s deployment with Ocean Right-Sizing suggestions
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: Ocean Right-Sizing remote action
        uses: tsahiduek/ocean-right-sizing-githubaction@v0.1
        id: remote-ocean-right-sizing-mutator
        env:
          SPOT_OCEAN_ID: ${{ secrets.OCEAN_ID }}
          SPOT_OCEAN_CONTROLLER: ${{ secrets.OCEAN_CONTROLLER }}
          SPOT_TOKEN: ${{ secrets.SPOT_TOKEN }}
          SPOT_ACCOUNT: ${{ secrets.SPOT_ACCOUNT }}
          ```
````

This action reads the deployment from `K8s/deployment.yaml` by default. You can specify multiple different deployment files by providing comma delimited field to the workflow of the name `K8s-yamls`. Example as follows:

````yaml
on: [push]

jobs:
  ocean_right_sizing_deployment_mutation:
    runs-on: ubuntu-latest
    name: Mutate K8s deployment with Ocean Right-Sizing suggestions
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: Ocean Right-Sizing remote action
        uses: tsahiduek/ocean-right-sizing-githubaction@v0.1.1
        id: remote-ocean-right-sizing-mutator
        env:
          SPOT_OCEAN_ID: ${{ secrets.OCEAN_ID }}
          SPOT_OCEAN_CONTROLLER: ${{ secrets.OCEAN_CONTROLLER }}
          SPOT_TOKEN: ${{ secrets.SPOT_TOKEN }}
          SPOT_ACCOUNT: ${{ secrets.SPOT_ACCOUNT }}
        with:
          K8s-yamls: "K8s/deployment.yaml;K8s/deployment2.yaml"
          ```
````
