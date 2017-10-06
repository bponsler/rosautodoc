from os.path import join

from formatConverters import FileExtension, MarkdownToHtml, MARKDOWN, HTML


class NodeInfo:
    """The NodeInfo class contains all the information pertaining to
    a single ROS Node. This keeps track of the published topics,
    subscribed topics, parameters, and services used or provided
    by this node.

    """

    def __init__(self, nodeName):
        """Create a NodeInfo object.

        * nodeName -- the name of the node

        """
        self.__nodeName = nodeName

        # Info about a node
        self.__params = []
        self.__pubs = {}
        self.__subs = {}
        self.__services = {}

    def getCleanName(self):
        """Get a clean name for this node so that it can be used
        as a filename.

        """
        # Create a node name that can be used as a filename
        cleanNodeName = self.__nodeName.replace("/", "_")
        if cleanNodeName.startswith("_"):
            cleanNodeName = cleanNodeName[1:]

        return cleanNodeName

    def addParam(self, param):
        """Add a parameter to this node.

        * param -- the parameter

        """
        if param not in self.__params:
            self.__params.append(param)

    def addPub(self, topic, pubType):
        """Add a published topic to this node.

        * topic -- the published topic
        * pubType -- the type of data

        """
        self.__pubs[topic] = pubType

    def addSub(self, topic, subType):
        """Add a subscribed topic to this node.

        * topic -- the subscription topic
        * pubType -- the type of data

        """
        self.__subs[topic] = subType

    def addService(self, service, serviceType):
        """Add a service to this node.

        * service -- the service
        * serviceType -- the type of service

        """
        self.__services[service] = serviceType

    def document(self, outputDir, docFormat=MARKDOWN):
        """Document the information pertaining to the nodes.

        * outputDir -- the directory where the documentation will be output
        * docFormat -- the desired format of the documentation

        """
        lines = [
            "# The %s node" % self.__nodeName,
            "",
        ]

        # Document parameters
        lines.extend([
            "## Parameters:",
            ])
        for param in self.__params:
            lines.append("- %s -- " % param)

        # Document services
        lines.extend([
            "",
            "## Services:",
        ])
        for name, serviceType in self.__services.iteritems():
            lines.append("- %s [%s] -- " % (name, serviceType))

        # Document subscriptions
        lines.extend([
            "",
            "## Subscribers:",
        ])
        for name, subType in self.__subs.iteritems():
            lines.append("- %s [%s] -- " % (name, subType))

        # Document publications
        lines.extend([
            "",
            "## Publishers:",
        ])
        for name, pubType in self.__pubs.iteritems():
            lines.append("- %s [%s] -- " % (name, pubType))

        cleanNodeName = self.getCleanName()
        extension = FileExtension.get(docFormat)
        filename = join(outputDir, "%s.%s" % (cleanNodeName, extension))

        # Convert the markdown format
        if docFormat == HTML:
            lines = MarkdownToHtml.convert(lines)

        # Write the data to the file
        fd = open(filename, "w")
        fd.write("%s\n" % "\n".join(lines))
        fd.close()


class RosDocWriter:
    """The RosDocWriter class manages data for a set of nodes
    and makes it possible to generate documentation for all of
    those nodes.

    """

    def __init__(self, nodeNames):
        """Create a RosDocWriter object.

        * nodeNames -- the list of node names to monitor (all nodes
                       will be monitored if the list is empty)

        """
        self.__nodeNames = nodeNames

        self.__nodes = {}
        for nodeName in nodeNames:
            self.__nodes[nodeName] = NodeInfo(nodeName)

    def addParam(self, nodeName, param):
        """Add a parameter to a node.

        * nodeName -- the node
        * param -- the parameter

        """
        if self.__hasNode(nodeName):
            self.__getNode(nodeName).addParam(param)

    def addPub(self, nodeName, topic, pubType):
        """Add a published topic to a node.

        * nodeName -- the node
        * topic -- the published topic
        * pubType -- the type of data

        """
        if self.__hasNode(nodeName):
            self.__getNode(nodeName).addPub(topic, pubType)

    def addSub(self, nodeName, topic, subType):
        """Add a subscribed topic to a node.

        * nodeName -- the node
        * topic -- the subscribed topic
        * subType -- the type of data

        """
        if self.__hasNode(nodeName):
            self.__getNode(nodeName).addSub(topic, subType)

    def addService(self, nodeName, service, serviceType):
        """Add a service to a node.

        * nodeName -- the node
        * service -- the service topic
        * serviceType -- the type of data

        """
        if self.__hasNode(nodeName):
            self.__getNode(nodeName).addService(service, serviceType)

    def document(self, outputDir, docFormat=MARKDOWN):
        """Document the information pertaining to the nodes.

        * outputDir -- the directory where the documentation will be output
        * docFormat -- the desired format of the documentation

        """
        for nodeName, node in self.__nodes.iteritems():
            print "    Documenting %s..." % nodeName
            node.document(outputDir, docFormat)

        # Write a manifest file to link to all other nodes, if there are
        # multiple nodes being documented
        if len(self.__nodes) > 0:
            print "Creating documentation manifest..."
            self.__writeManifest(outputDir, docFormat)

    def __writeManifest(self, outputDir, docFormat=MARKDOWN):
        """Write the documentation manifest file which links to the
        documentation for all nodes.

        * outputDir -- the directory where the documentation will be output
        * docFormat -- the desired format of the documentation

        """
        extension = FileExtension.get(docFormat)
        filename = "index" if docFormat == HTML else "README"
        manifest = join(outputDir, "%s.%s" % (filename, extension))

        lines = [
            "# ROS system documentation"
            "",
            "## Nodes",
            "",
        ]

        # Add links to all nodes in alphabetical order
        sortedNodes = sorted(self.__nodes.keys())
        for nodeName in sortedNodes:
            node = self.__nodes[nodeName]
            cleanNodeName = node.getCleanName()

            link = "- [%s](%s.md)" % (nodeName, cleanNodeName)
            if docFormat == HTML:
                link = '- <a href="%s.html">%s</a>' % (cleanNodeName, nodeName)

            lines.append(link)

        # Convert the markdown format
        if docFormat == HTML:
            lines = MarkdownToHtml.convert(lines)

        # Write the data to the manifest file
        fd = open(manifest, "w")
        fd.write("%s\n" % "\n".join(lines))
        fd.close()

    def __hasNode(self, nodeName):
        """Determine if this node is being monitored.

        * nodeName -- the node

        """
        return (len(self.__nodeNames) == 0 or nodeName in self.__nodes)

    def __getNode(self, nodeName):
        """Get the NodeInfo object.

        * nodeName -- the name of the node

        """
        if nodeName not in self.__nodes:
            self.__nodes[nodeName] = NodeInfo(nodeName)
        return self.__nodes[nodeName]
