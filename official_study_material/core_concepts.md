agent : a software entity that communicates via messages, maintains its own state, and performs actions 
in response to received messages or changes in its state.

Many software systems can be modeled as a collection of independent agents that interact with one another.

These systems, composed of multiple interacting agents, are referred to as multi-agent applications.

1. Standalone Agent Runtime

- Standalone runtime is suitable for single-process applications 
- where all agents are implemented in the same programming language and running in the same process. 
- In the Python API, an example of standalone runtime is the SingleThreadedAgentRuntime.

- Developers can build agents quickly by using the provided components including:    
    - routed agent, 
    - AI model clients, 
    - tools for AI models, 
    - code execution sandboxes, 
    - model context stores, and more. 
- They can also implement their own agents from scratch, or use other libraries.

2. Distributed Agent Runtime

- Distributed runtime is suitable for multi-process applications 
- where agents are implemented in different programming languages and running in different processes. 

- A distributed runtime, as shown in the diagram above, consists of a host servicer and multiple workers. 
- The host servicer facilitates communication between agents across workers and maintains the states of connections. 
- The workers run agents and communicate with the host servicer via gateways. 
- They advertise to the host servicer the agents they run and manage the agents’ lifecycles.


Application Stack




















