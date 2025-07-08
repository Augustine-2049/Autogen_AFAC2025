'''
core concepts : agents, agent runtime, message, communication.

agent in AutoGen : entity defined by the base interface Agent. 
It has a unique identifier of the type AgentId, a metadata dictionary of the type AgentMetadata.

In most cases, you can subclass your agents from higher level class RoutedAgent 
which enables you to route messages to corresponding message handler specified with message_handler() decorator 
and proper type hint for the message variable. An agent runtime is the execution environment for agents in AutoGen.


'''