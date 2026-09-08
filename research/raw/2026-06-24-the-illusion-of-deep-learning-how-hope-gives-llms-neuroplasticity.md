---
title: "The Illusion of Deep Learning: How HOPE Gives LLMs Neuroplasticity"
author: "Fabio Yáñez Romero"
author_url: "https://medium.com/@fabioyanezromero"
source: "https://aiadvances.org/the-illusion-of-deep-learning-how-hope-gives-llms-neuroplasticity-283e6a145281"
published: "2026-06-24"
fetched: "2026-09-08"
reading_time_min: 15.8
tags: ["machine-learning", "artificial-intelligence", "large-language-models", "deep-learning", "neural-networks"]
member_only: true
body_source: "medium-session"
---

# The Illusion of Deep Learning: How HOPE Gives LLMs Neuroplasticity

### Beyond static weights: Discover how HOPE, Living Gates, and Delta Gradient Descent are building the first truly self-evolving neural networks.

Imagine a genius scholar who masters the knowledge of thousands of books in a single day, only to wake up the next morning with zero long-term memory. They can hold a brilliant conversation using their working memory, but once the chat ends, they forget you ever existed. It is a **cognitive Groundhog Day.**

![The evolution of AI memory: From cold, static weights suffering from “anterograde amnesia” to a living, neuroplastic ecosystem anchored by a single stable lens.](https://miro.medium.com/v2/1*Hm8dki2SEFyqQuUcBYT3cw.png)

This concept, clinically known as ***anterograde amnesia***, is the inability to create and consolidate new memories after a certain point. The patient is forced to rely on their long-term memory until the onset of the condition, and thereafter they depend entirely on short-term working memory, which vanishes after a short while.

This perfectly illustrates what is happening with language models right now and gives us a clear idea of the monumental challenges AI laboratories face in achieving the next level of Artificial Intelligence.

In the AI world, we can interpret long-term knowledge — consolidated up to a certain point — as the **training dynamics**, including pre-training, fine-tuning, instruction tuning, etc. Once deployed, these underlying weights are frozen.

On the other hand, the unconsolidated short-term memory is the actual attention mechanism operating during inference. This enables ***in-context learning* capabilities **— in other words, the ability to adapt to a specific task given context (specific prompts, skills, few-shot samples, chain-of-thought reasoning) without modifying the model’s weights. However, these in-context learning capabilities are totally bound to the current context window and disappear as soon as it resets.

> What if this limitation is not an engineering hurdle, but a fundamental flaw in how we conceptualise deep learning?

A groundbreaking framework called the **Nested Learning** paradigm suggests exactly that. It proposes a radical shift to liberate models from anterograde amnesia and achieve true artificial neuroplasticity using self-referential architectures such as **HOPE**.

Following this narrative, to understand how HOPE achieves this, we must first look at the precursor that laid the groundwork. **Titans** is an architecture that has already tried to solve this problem in regular Transformers by including Long-Term Memory Modules that can adapt their knowledge during inference. While this approach was revolutionary, it still had much potential yet to be unlocked to truly shine.

## **📌 TL;DR: The Neuroplastic Revolution**

- **The Nested Learning Paradigm:** Deep learning components, including optimisers such as AdamW, are associative memory modules that operate and update at different frequencies.
- **“Living Gates” Over Attention:** The HOPE architecture replaces traditional static attention with dynamic modules that self-generate their learning and forgetting rates, as well as internal goals, in real time.
- **Neuroplasticity:** An internal optimiser, called **Delta Gradient Descent (DGD)**, ephemerally sculpts the model’s weights during the forward pass, enabling the AI to adapt to the immediate context.
- **Chunk-Wise Parallelisation:** To avoid computational collapse, DGD processes entire blocks of past tokens simultaneously using matrix algebra, making real-time weight mutation highly efficient.
- **The Cognitive Anchor:** The Query Projection (*Wq*​) remains the sole frozen element. It acts as a stable reading “lens” so the global optimiser (AdamW) can cleanly backpropagate errors without causing a chaotic feedback loop.

## **Titans: The Precursor to a Living AI**

Titans was a really new challenger to the actual Transformer in terms of memorisation and avoiding catastrophic forgetting. We already talked about it exhaustively in the following post, so you might find it useful; we will make a small summary nonetheless:

[[**Titans: How Google Taught AI to Surprise, Forget, and Remember**
*Google’s new memory system for language models — and why attention alone was never enough*ai.gopubby.com](https://ai.gopubby.com/titans-how-google-taught-ai-to-surprise-forget-and-remember-b4bd497c0789)](https://ai.gopubby.com/titans-how-google-taught-ai-to-surprise-forget-and-remember-b4bd497c0789)

This model introduced the idea of a **memory module**, which includes any architecture used to store and retrieve memory and can be updated over time.

In this sense, within the paradigm of memory modules, the attention mechanism can be considered a kind of memory module for **short-term memory**, focusing directly on the current sequence that populates the model’s context and nothing else.

> This makes sense if we consider the actual KV cache that populates as long as the sequence is alive and affects the knowledge retrieved by the entire model.

To complement the attention mechanism, Titans introduces a **Long-Term Memory Module (LMM)**, which stores and retrieves information from an MLP in different ways and makes it available to the model for use with attention, combining both short-term and long-term memory into a transformer-like model. There are several reasons why Titans, specifically with this LMM, can be considered the precursor of nested learning:

- It has an inner training objective learned directly from transformations of the hidden state, which is considered a form of **self-supervised meta-learning**. So, somehow, it is learning how to learn, as Nested Learning proposes.
- It can **learn at test time and during inference**, as this internal objective for learning creates the keys and values needed for training the LMM and also retrieves the query at inference to access the model’s long-term memory. This can be interpreted as the **neuroplasticity** introduced in Nested Learning.
- As mentioned, **this model differentiates among memory modules**, specifically the short-term (attention mechanism), the LMM, and the persistent memory module (learned embeddings).

![The original Titans Memory Module. A revolutionary step for test-time memorisation, yet still constrained by frozen projections and rigid learning rules.](https://miro.medium.com/v2/1*CJUgWXfmNyxNgmO-i2hAVg.png)

And this is a great improvement over the Transformer, as the newly considered memory modules help fix the amnesia present in the original Transformer model, but **the versatility Titans introduces is relative**.

### **The Illusion of Versatility: Why Titans Was Not Enough**

The main limitation in Titans that Hope tries to fix, with the introduction of Nested Learning, is more versatility for the model, trying to mimic the neuroplasticity concept in several ways; let’s enumerate them based on the actual limitations discussed by Nested Learning over Titans:

- **Frozen Projections**: the introduction of memory modules that are able to learn at test time is quite impressive, but the actual linear transformations that bring the keys and values, which are the actual bridge between the LMM and the backbone model, are frozen once the upper training is finished. This reduces the versatility of the introduced memory module.
- **All the hyperparameters for the memory modules follow the traditional schedule**, including cosine annealing to determine the learning rate and deterministic weight decay based on the gradient. This goes against the neuroplasticity idea.
- **The gradient**, as the signal that determines the update of the different components inside the model, **is tied to each specific token the model is processing individually**, but the language is a sequential structure, and it does not make sense that the update rule is determined independently for each token, as if the surrounding tokens have no effect on it.

So, Titans was able to memorise, but it was ultimately trapped in static rules and failed to represent how a brain should work.

## **The Blind Spot of AdamW**

AdamW is derived from Gradient Descent (GD), which computes the error between the prediction and the actual label using dot-product similarity, and updates the parameters in the direction of the error.

This dot-product similarity treats each gradient associated to each token as an individual cell in the entire text sequence for optimisation, but the language model is tied to the entire sequence, so considering it per token individually makes no sense.

AdamW improves gradient descent by adding momentum to the gradient direction GD already provided, based on prior updates. This means the update cannot be too aggressive, as it could negatively influence the result, and that the model will learn from small deviations that would otherwise be ignored.

But we still have the problem that AdamW does not account for the sequential relationships among tokens in a sequence. So this optimiser alone is not enough to learn the implicit relations between different tokens.

HOPE, in this sense, introduces the use of living gates and DGD to address this problem, designing a nested optimisation process that coordinates seamlessly with AdamW, as we will see.

> AdamW can be considered a new type of associative memory in the model, where an operator translates the variance of previous gradients (keys) into more stable updates (values).

> AdamW interprets the error signal as independent cells in a sequence

## **Living Gates: Replacing Static Attention**

HOPE introduces a modified Titans architecture to replace the original attention mechanism. This architecture can be considered a Titans LMM with “living gates” that grant the expected neuroplasticity to the model.

![The anatomy of HOPE: Replacing static attention with a living ecosystem where hyperparameters and internal goals are self-generated in real-time.](https://miro.medium.com/v2/1*XYGjHce3yeXdB48zJ4otxw.png)

These living gates are new modules that determine the learning and forgetting rates, as well as the key and value projections for every token the model processes. With this, the model can adapt automatically to the current context and determine its own learning dynamics.

If we go into the definition of an associative memory module, based on Nested Learning:

> An associative memory module is an operator that learns how to map specific keys to their values for a given task. So every module that learns some kind of mapping in the model is, in fact an associative memory module, including the traditional attention, and the long-term memory module.

We can consider these new modules as associative memory modules that translate token embeddings into appropriate hyperparameters for each token, avoiding the generic hyperparameters we typically use during LLM training.

These new modules **operate in parallel**, directly on the token embeddings produced by the tokeniser, and provide these hyperparameters to the modified Titans Memory Module, which we will call the **central memory module;** ultimately, it acts the same way as any other living gate.

However, these living gates first need to learn; without any training, those modules are not ready to provide the hyperparameters the model needs. To this end, we will draw on traditional learning techniques and optimisers (e.g., AdamW) for language models in the upper optimisation step until each module can perform its task effectively. In this sense, the upper optimiser will help us learn the optimal initial state for the weights before neuroplasticity is applied.

### **The Triple Heartbeat: Living Gates in Action**

We can think about the living gates as parallel MLPs that are located just after the tokeniser, and determine the actual hyperparameters for the current state based on the previous one, solving the limitations of AdamW and backpropagation when combined with Delta Gradient Descent (DGD), a new type of nested optimisation discussed in the next section.

All the living gates perform three different forward passes:

- The first one processes the token-specific embedding generated by the tokeniser, using the previous gate state (*t-1*) to obtain the corresponding **global hyperparameters for the model**. In this case, the Global Key (k*t*), Global Value (V*t*), Learning Rate (𝜂𝑡), and Retention Rate (αt*) a*re associated with that specific token.
- The second one uses the **Global Value **as input to each of those gates to obtain the **Internal Value for that specific module**, so the module can use its own intuition to update its objective later with DGD.
- The third one uses the **Global Key** as input to each of the living gates **to return the prediction based on the accumulated state up to (*t-1*)**, so we can compare it with the internal value as a measure of surprise in DGD, as we will discuss in the next subsection.

> It’s like a triple heartbeat in a nested optimisation process capturing the surprise for the knowledge integration

![The Triple Heartbeat: How the Living Gates interrogate the frozen state multiple times to calculate the “surprise” signal before applying any mutation.](https://miro.medium.com/v2/1*nIlW8M0NHC-gRtyCJM8Q-g.png)

Next, the newly introduced optimiser, DGD, can generate subsequent states from the initial weights that address the neuroplasticity problem, thereby enabling the model to adapt quickly to the current context.

## **Delta Gradient Descent: The Engine of Neuroplasticity**

To address the sequentiality of the learning signal and neuroplasticity**, Delta Gradient Descent (DGD) **is introduced as an internal optimiser that operates during the model’s forward pass, creating ephemeral states for each living gate and the central memory module, which can be updated in parallel.

For DGD to work, a single ephemeral copy of the current weight matrix is created for each living gate. DGD will work on that **ephemeral copy** maintained for neuroplasticity only, which is **included in the computational graph** for later use by AdamW during the persistent update.

![True neuroplasticity without catastrophic forgetting: DGD sculpts an ephemeral working clone (Mₜ​) while the persistent weights remain safely locked during the forward pass.](https://miro.medium.com/v2/1*zJMpcRL8fDAG6VKyHpncDA.png)

**The parallel updating** is possible because each of those ephemeral copy updates depends only on its Internal Value (v*t*), determined individually using the Global Value (V*t*), and on the Global Key (k*t*) obtained during the first forward pass with the living gates, as we mentioned in the previous section.

This nested optimisation coordinates with AdamW without getting in each other’s way. It is like giving the sequential context that DGD can capture to the more general AdamW, which, by itself, is blind to the entire sequence and would otherwise focus only on the current elements.

> Backpropagation has a linear dependency, from the last module to the first one to update everything in order, DGD does not need that due to the internal objective of each module.

Now, let’s talk about how DGD is performed step by step, its interpretation of neuroplasticity, and how it can capture sequential interactions.

### **Erase & Write: The Math Behind the Mutation**

DGD drops the dot product used to update each parameter in these living gates and instead performs L2 regression (mean squared error), updating the living gate and the central memory’s ephemeral copies, using the following equation:

![](https://miro.medium.com/v2/1*VhgGZYtwomBIhwSEmznV3Q.png)

This equation might seem intimidating, but in the end, it is performing two different actions: the first term is the memory erasing, which can be categorised into **global and targeted erase**, whereas the second term is the proper **memory writing**:

- **The global memory-erasing *M*□,**ₜ₋₁** (*α***ₜ** I) **takes the global retention rate obtained for this step (***α***ₜ) and decays each weight in the copy by that proportion.
- **The targeted memory-erasing *M*□,**ₜ₋₁** (**−ηₜkₜkₜᵀ**) **uses the initial global key (**k*t***), multiplied by its transpose, to create a rank-1 matrix that serves as a filter, indicating the direction of the context for the actual token in the copy. Then the general learning rate (***ηt***) is used as the magnitude of the targeted erasing. Effectively, it clears the space we need to use for the update.

> The rank-1 matrix for the current token in the targeted memory erase is crucial. It means each of the vectors from that matrix are linearly dependent from each other. This can be semantically interpreted as every component in the matrix is related with only that specific token and cannot degrade other tokens memory.

> The targeted memory erasing using the learning rate as magnitude instead of the retention rate might be confusing, but it makes all the sense considering that a high learning rate means we need to update a lot the knowledge we have from a specific concept, and if we have a limited space for that concept in our weights we shall free a proportional space before the update.

- **The memory writing *ηt*​∇L(*M*□,**ₜ₋₁**;k**ₜ**,v□,**ₜ**)** rescues the **surprise term** already introduced in Titans as the gradient based on the loss function (∇L). However, in this case, the surprise is based on the quadratic error between the network’s prior state (***M*□,**ₜ₋₁) using the global key (**k**ₜ) and the current internal value (**v□,**ₜ).

Notice that the Global Key, in conjunction with the living gate initial copy, indicates the region associated with the specific token that needs to be modified to update the knowledge, as seen in targeted memory erasure and memory writing.

As a conclusion from the DGD optimisation objective, we can see that it is intended to locate the different regions for each token and update its knowledge without degrading the knowledge of other regions belonging to other tokens. As this is performed on every forward pass, the neuroplasticity based on the current context that is going into the model is guaranteed.

But all of this has been explained for a specific token, whereas, as we discussed previously, the language has a linear dependency, and thus it makes sense to consider a context window in any of those steps rather than only one token.

### **Chunk-Wise Parallelisation: Beating the Sequential Bottleneck**

As mentioned, having a learning signal associated with each token based not solely on that token but on a sliding context is crucial in natural language. In this case, this is moving from the delta to the omega rule.

> If the model learned word by word independently, it could get a high bias, focusing on local noise and giving weights that make no sense to the different tokens; for instance, an article before a substantive might get too much weight, whereas the semantic impact of that word is negligible

**The delta rule** takes only one token to determine the global parameters and all their respective forward passes to obtain the internal values and compare them with the old state, as discussed in the previous section.

The **Omega Rule** goes one step further. Instead of processing one token embedding per module per step, it evaluates an entire local context of past data simultaneously. To avoid processing tokens strictly one by one (which would be computationally prohibitive), the architecture uses a chunk-wise parallelisation trick.

Instead of applying a pooling operation to squash the chunk into a single vector, DGD leverages matrix algebra to process all tokens independently yet simultaneously. The parallelisation can be conceptualised using the previously mentioned three forward passes:

- The first forward pass uses the token embedding to get the global hyperparameters. In this case, we can pass a matrix representing the token embeddings across the entire chunk and create matrices containing the global hyperparameters.
- The second forward pass will again create a list of internal values, one for each token in the chunk.
- The third forward pass will use the global keys matrix to obtain the internal objective predicted as a new matrix.

After this, DGD can perform the same operation on matrices that can be parallelised, rather than on vectors representing individual tokens.

## The Cognitive Anchor: Bridging the Micro and the Macro

With only the DGD optimisation on the living gates, each module might be operating in its own mind without seeing the entire picture, so it might be working toward the wrong general objective and thus be unable to predict the correct next word in the sequence.

> We need a bridge between the internal objective and the general objective

In this case, the general objective is the traditional one we have in the upper optimisation process, typically next-token prediction during pretraining, fine-tuning, or instruction tuning.

To solve this specific problem and orchestrate the full training, AdamW will capture the DGD signal and update all weights during backpropagation, accounting for changes in the ephemeral states and converging into the optimal initial state for those living gates.

In the case of the fully self-referential HOPE that uses DGD in each module, this applies to all hyperparameter calculations and projections, except for the Query Projection (qₜ), which serves as a vital “cognitive anchor” and the ultimate bridge between DGD and AdamW.

![The Cognitive Anchor: AdamW traverses the ephemeral chaos to gather context, but uses the frozen Query Projection as a clean highway to permanently update the model’s baseline intuition.](https://miro.medium.com/v2/1*Uyk4X_ZF3XEmw7uWMXI5ew.png)

### **Why the Query? The Law of Read vs. Write**

To understand exactly why the Query (qₜ) takes on this static role rather than the Keys (kₜ) or Values (vₜ), we must consider the fundamental difference between the read and write mechanisms in an associative memory.

Keys and Values are the driving force behind neuroplasticity: the Key defines how information is indexed or linked, and the Value defines which concept is being stored. If we were to freeze the projections of the keys or values, we would force the DGD engine to archive information according to rigid, pre-programmed rules, thereby destroying the model’s ability to restructure its knowledge in real time. For AI to truly adapt to context, it needs complete freedom to mutate its own latent values and indices.

The Query, by contrast, is the reading mechanism. It does not alter the memory; it simply accesses the mutated network to extract the final response. If the query projection were also mutating in real-time, the network could fall into an uncontrollable feedback loop, losing a stable reference to search its own memory. By maintaining the Query Projection as the sole non-adaptive projection in HOPE, an unbreakable contract is established between the two learning frequencies: AdamW will always use a static ‘lens’ or ‘torch’ to search for answers, whilst the DGD engine has complete freedom to reorganise keys and values internally.

> If the extracted response turns out to be incorrect in relation to the overall objective, the error of the model’s output with respect to the objective is calculated. It is here that backpropagation travels from the outputs, travelling backwards through the entire model, until it reaches the query projection. It serves as a clean conduit for injecting this penalty. AdamW uses this anchor to modify the persistent parameters, ensuring that the controlled chaos of local neuroplasticity always ultimately serves the model’s overall objective.

### **AdamW: The Ultimate Wrapper**

AdamW wraps the living gates, the central memory module (also considered a living gate, as mentioned before), and the **Continuum Memory System** (**CMS)**, which serves as a substitute for the usual MLPs in a Transformer in this architecture. This means CMS is the module that saves and integrates long-term memory.

## **The Other Half: Teasing the Continuum Memory System**

AdamW wraps the living gates, the central memory module (also considered a living gate, as mentioned before), and the Continuum Memory System (CMS), which serves as a substitute for the usual MLPs in a Transformer in this architecture. This means CMS is the module that saves and integrates long-term memory.

We have come a long way from the limitations of the original Titans model. Through the lens of the Nested Learning paradigm, we have seen how HOPE transforms the traditional static architecture into a living ecosystem:

- By replacing the classic attention mechanism with **Living Gates**, the model can now self-generate its own hyperparameters and internal goals.
- Thanks to the **Delta Gradient Descent (DGD)** engine operating in parallel over chunks, the network acquires true neuroplasticity, ephemerally sculpting its weights to adapt to the context efficiently without collapsing the servers.
- Finally, we have discovered that the **Query Projection** serves as the perfect cognitive anchor, allowing the upper optimiser (AdamW) to continue correcting the model’s base intuition without undermining its short-term creative freedom.

> The scholar can finally learn within the conversation. Whether they wake up tomorrow having kept it is the question the CMS exists to answer

Real-time adaptation is only one part of what makes a brain intelligent. As mentioned, HOPE comprises not only this modified attention mechanism but also the **Continuum Memory System (CMS)**.

This component, the MLP’s substitute and the one responsible for long-term memory integration, abandons the idea of static layers in favour of a spectrum of memories updating at different frequencies, just like human brainwaves.

But it introduces so many changes and new paradigms that it must be considered in a new blog, as the amount of information added here is already overwhelming.

So, stay tuned for the next post if you want to decipher the CMS and the entire Nested Learning paradigm!

> **Understanding should not be a luxury reserved for specialists.**
My goal is to make frontier AI and machine learning research accessible through clear, tutorial-style explanations.

> If this piece helped you think more clearly about the topic, showing support with **claps** or a **subscription** genuinely helps keep this work going.

> You’re always welcome to connect with me on [**LinkedIn](https://www.linkedin.com/in/fabio-yanez/)**, where I share more writing and ideas in the same spirit.
