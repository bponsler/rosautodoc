import socket
import argparse
from os.path import exists, abspath, curdir

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from docWriter import RosDocWriter
from formatConverters import MARKDOWN, SUPPORTED_DOC_FORMATS

import rosgraph


class RosMasterFunctions:
    """The RosMasterFunctions class provides a class that exports all
    of the XMLRPC functions provided by the ROS master. This class
    intercepts calls to some of those methods in order to keep track
    of the publishers, subscribers, services, and parameters used by
    nodes. This class then makes it possible to generate documentation
    for that information.

    """
    RosMasterHost = "localhost"
    RosMasterPort = 11311

    # List of all methods supported by the ROS master
    RosMasterMethods = [
        "getPid",
        "registerService",
        "unregisterService",
        "registerSubscriber",
        "unregisterSubscriber",
        "registerPublisher",
        "unregisterPublisher",
        "lookupNode",
        "getPublishedTopics",
        "getTopicTypes",
        "getSystemState",
        "getUri",
        "lookupService",
        "deleteParam",
        "setParam",
        "getParam",
        "searchParam",
        "subscribeParam",
        "unsubscribeParam",
        "hasParam",
        "getParamNames",
    ]

    # List of ROS parameters to ignore
    FilterParameters = [
        "/tcp_keepalive",
        "/use_sim_time",
    ]

    # List of published ROS topics to ignore
    FilterPublishedTopic = [
        "/rosout",
    ]

    # List of subscribed ROS topics to ignore
    FilterSubscribedTopics = [
    ]

    # List of ROS services to ignore
    FilterServices = [
    ]

    def __init__(self, nodeNames):
        """Create a RosMasterFunctions object.

        * nodeNames -- the list of node names to document

        """
        masterUri = 'http://%s:%s' % (self.RosMasterHost, self.RosMasterPort)

        # Create an XMLRPC client to connect to the ROS master
        self.__client = xmlrpclib.ServerProxy(masterUri)

        # Register all ROS master methods with this class to allow custom
        # functionality to be executed prior to sending the data to the
        # ROS master
        for method in self.RosMasterMethods:
            wrapper = self.__getWrapper(method)
            setattr(self, method, wrapper)

        self.__nodeNames = nodeNames

        # Add a prefix slash if one is not given
        for i in range(len(self.__nodeNames)):
            if not nodeNames[i].startswith("/"):
                self.__nodeNames[i] = "/%s" % nodeNames[i]

        self.__docWriter = RosDocWriter(self.__nodeNames)

    def document(self, outputDir, docFormat=MARKDOWN):
        """Document the information pertaining to the nodes.

        * outputDir -- the directory where the documentation will be output
        * docFormat -- the desired format of the documentation

        """
        self.__docWriter.document(outputDir, docFormat)

    def __getWrapper(self, method):
        """Return a XMLRPC wrapper function which can optionally intercept
        a call to the given ROS master XMLRPC method.

        * method -- is the desired ROS master XMLRPC function to call

        """
        def wrap(*args):
            """Callback function for an XMLRPC function.

            * args -- the method input arguments

            """
            # If this class has a method callback registered, then
            # make sure we call the callback. Otherwise, just pass
            # the call through to the true ROS master server
            try:
                callback = "_%s" % method
                if hasattr(self, callback):
                    callbackFn = getattr(self, callback)
                    callbackFn(*args)
            except Exception, e:
                import traceback
                traceback.print_exc()

            # Pass the call through to the ROS master
            masterFn = getattr(self.__client, method)
            return masterFn(*args)

        return wrap

    def _registerPublisher(self, callerId, topic, topicType, callerApi):
        """Intercept callback for the registerPublisher function.

        * callerId -- the caller id (calling node name)
        * topic -- the publisher topic
        * topicType -- the type of the publisher
        * callerApi -- the caller API string

        """
        if topic not in self.FilterPublishedTopic:
            self.__docWriter.addPub(callerId, topic, topicType)

    def _registerSubscriber(self, callerId, topic, topicType, callerApi):
        """Intercept callback for the registerSubscriber function.

        * callerId -- the caller id (calling node name)
        * topic -- the subscriber topic
        * topicType -- the type of the subscriber
        * callerApi -- the caller API string

        """
        if topic not in self.FilterSubscribedTopics:
            self.__docWriter.addSub(callerId, topic, topicType)

    def _registerService(self, callerId, service, serviceApi, callerApi):
        """Intercept callback for the registerService function.

        * callerId -- the caller id (calling node name)
        * service -- the service topic
        * serviceApi -- the service API string
        * callerApi -- the caller API string

        """
        if service not in self.FilterServices:
            # The type of the service is not included in the XMLRPC call
            self.__docWriter.addService(callerId, service, "UNKNOWN")

    def _getParam(self, callerId, key):
        """Intercept callback for the getParam function.

        * callerId -- the caller id (calling node name)
        * key -- the parameter name

        """
        if key not in self.FilterParameters:
            self.__docWriter.addParam(callerId, key)

    def _hasParam(self, callerId, key):
        """Intercept callback for the hasParam function.

        * callerId -- the caller id (calling node name)
        * key -- the parameter name

        """
        if key not in self.FilterParameters:
            self.__docWriter.addParam(callerId, key)

    def _setParam(self, callerId, key, value):
        """Intercept callback for the setParam function.

        * callerId -- the caller id (calling node name)
        * key -- the parameter name
        * value -- the parameter value

        """
        if key not in self.FilterParameters:
            self.__docWriter.addParam(callerId, key)


class RosMasterProxy:
    """The RosMasterProxy class implements an XMLRPC proxy server to
    intercept calls to the ROS master. These calls are monitored and
    documentation can be generated containing that information.

    """

    def __init__(self,
                 nodeName,
                 hostname="localhost",
                 port=33133,
                 verbose=False):
        """Create a RosMasterProxy object.

        * nodeName -- the name of the node to document
        * hostname -- the hostname for the proxy server
        * port -- the port for the proxy
        * verbose -- true for verbose mode

        """
        # Create the XMLRPC server
        self.__server = SimpleXMLRPCServer(
            (hostname, port),
            logRequests=verbose)

        # Register XMLRCP introspection methods like:
        #     system.listMethods, system.methodHelp and system.methodSignature
        # NOTE: These are not supported by the proper ROS master
        self.__server.register_introspection_functions()

        # Support multi-call methods which are used by roslaunch
        self.__server.register_multicall_functions()

        # Register the XMLRPC functions to support the ROS master API
        self.__masterFunctions = RosMasterFunctions(nodeName)
        self.__server.register_instance(self.__masterFunctions)

    def start(self):
        """Start the RosMasterProxy"""
        # Run the server's main loop
        self.__server.serve_forever()

    def document(self, outputDir, docFormat=MARKDOWN):
        """Document the information pertaining to the nodes.

        * outputDir -- the directory where the documentation will be output
        * docFormat -- the desired format of the documentation

        """
        self.__masterFunctions.document(outputDir, docFormat)


def main():
    """The main function for the rosautodoc application."""
    parser = argparse.ArgumentParser(
        description='Automatically document the API for a a ROS node.')
    parser.add_argument(
        'nodes',
        metavar="node",
        type=str, nargs='*',
        help='The name of the nodes to document. If empty, ' +
        'all nodes will be documented')
    parser.add_argument(
        '--output-dir',
        type=str,
        default=abspath(curdir),
        help='The directory where documentation should be written')
    parser.add_argument(
        '--proxy-port',
        type=int,
        default=33133,
        help='The port to use for the ROS master proxy server')
    parser.add_argument(
        '--doc-format',
        type=str,
        default=MARKDOWN,
        help="The format of the documentation to generate " +
        "(%s)" % ", ".join(SUPPORTED_DOC_FORMATS))

    args = parser.parse_args()

    # Grab command line arguments
    nodeNames = args.nodes
    outputDir = args.output_dir
    proxyPort = args.proxy_port
    docFormat = args.doc_format.lower()

    # Make sure the format is valid
    if docFormat not in SUPPORTED_DOC_FORMATS:
        print "ERROR: unknown doc-format argument: %s" % docFormat
        exit(2)

    # Ensure that the output directory exists
    if not exists(outputDir):
        print "ERROR: the output directory does not exist: %s" % outputDir
        exit(3)

    # Make sure the ROS master is running
    try:
        rosgraph.Master('/rostopic').getPid()
    except socket.error:
        print "ERROR: failed to communicate with the ROS master!"
        exit(4)

    # Create the ROS master proxy node
    masterProxy = RosMasterProxy(nodeNames, port=proxyPort)

    try:
        print "Starting server..."
        masterProxy.start()
    except (KeyboardInterrupt, SystemExit):
        pass

    # Document the information about the node
    print "Documenting..."
    masterProxy.document(outputDir, docFormat=docFormat)
