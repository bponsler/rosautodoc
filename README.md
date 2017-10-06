# rosautodoc

The rosautodoc project provides a python executable that can automatically
generate documentation for ROS nodes that are running on the system.

## Installation

Follow these instructions to download and install this project:

    git clone https://github.com/bponsler/rosautodoc
    cd rosautodoc
    sudo python setup.py install

## How does this work?

The rosautodoc script creates a proxy server that stands between a ROS system and the
ROS master to intercept all requests made by nodes. This allows the proxy server to
keep track of all publishers, subscribers, parameters, and services used by each
node and then use this information to create documentation for the node.

## Usage

This section describes how to use this project to automatically generate documentation.

    $ rosautodoc --help --doc-format=html --output-dir=/tmp/test_doc
    usage: rosautodoc [-h] [--output-dir OUTPUT_DIR] [--proxy-port PROXY_PORT]
                      [--doc-format DOC_FORMAT]
                      [node [node ...]]

    Automatically document the API for a a ROS node.

    positional arguments:
      node                  The name of the nodes to document. If empty, all nodes
                            will be documented

    optional arguments:
      -h, --help            show this help message and exit
      --output-dir OUTPUT_DIR
                            The directory where documentation should be written
      --proxy-port PROXY_PORT
                            The port to use for the ROS master proxy server
      --doc-format DOC_FORMAT
                            The format of the documentation to generate (markdown,
                            html)

# Examples

First, run the ROS master in one terminal (using the default master URI http://localhost:11311):

    roscore

Next, run the auto doc script in another terminal:

    mkdir /tmp/my_documentation
    rosautodoc --port=33133 --output=/tmp/my_documentation

Finally, run your node in another terminal, and be sure to connect it to the same port that the rosautodoc script is using:

    export ROS_MASTER_URI=http://localhost:33133
    rosrun my_package my_node

Once your node has finished starting up, you can stop the rosautodoc process which will
write one documentation file for every node on the system. The documentation will be
located in the /tmp/my_documentation directory.

Alternatively, you can document only a specific node:

    rosautodoc --port=33133 --output=/tmp/my_documentation /ns/my_node_name
