The context window is the entire input a large language model receives when generating output.

It contains everything that defines a conversation with a language model: your messages, the model’s replies, any tool calls, and even the thinking blocks the model outputs to “reason”.

The longer the conversation, the more there is in the context window.

Each time you send a new message, the message is added to the context window and the entire thing sent to the model:

Inference adds to the context window
The model then “reads” all of the conversation in the context window, not just your new message, and generates a response. Then, on the next turn, when you reply to the model’s response, the model’s response and your new message are added to the conversation:

The longer the conversation, the more there is in the context window
Yes, everything that happens between you and a model goes into the context window, including the tool calls. It’s all represented as text, too.

If you ask the model to run a bash command your message goes in the context window. The model’s response with its confirmation that it wants to run the bash tool on your machine goes in there too, including the input parameters to the tool. Then, the bash command is executed on your machine, the results go in the context window, and it’s all sent back up again:

Inference adds to the context window
This is how the context window fundamentally works, regardless of which model, or which chat application, or which agent you use.

Equally fundamental are the following three things you should know about the context window:

It can only get so big. Different language models have different limits for how much context they can run inference on, but all have one. That means every conversation with a model will, at some point, run into a limit and can’t continue: the model can’t accept more input than what’s already in the conversation.

Everything’s multiplied with everything else. To simplify drastically: in order to run inference, all the text in the context window is turned into tokens and tokens are, essentially, numbers. As part of running inference, the model then multiplies every token with every other token. That means: everything in the context window has an influence on the output. Some words and tokens have more influence than others, but everything counts to some extent. That’s why you don’t want to have text in your context window that you don’t want to influence the result.

Quality degrades: the more context, the worse the results. Most models provide better results with less context. There are exceptions and nuances to this idea, but, generally speaking, for the best results you should try to keep your conversations short & focused. The longer your conversation goes on, the higher the chances are the model goes “off the rails”: hallucinating things that don’t exist, failing to do the same things over and over again, declaring victory while standing on a mountain of glass shards.

The context window is important. And it’s important to care about what’s in it. It not only influences the outcome of your conversation with the agent, the conversation is the outcome.

stolen drom: https://ampcode.com/guides/context-management