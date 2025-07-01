# Rental Village Social Bot: Technical Application Overview

This document provides a detailed technical overview of the Rental Village Social Bot's content generation workflow, emphasizing the mechanisms of AI guidance and control. It serves as a foundational reference for developers and identifies potential areas for system enhancement.

## 1. Core Workflow Orchestration: `src/suggest_content.py`

The application's primary execution flow is orchestrated by `src/suggest_content.py`. This script acts as the central coordinator, responsible for gathering all necessary contextual data, invoking AI models for content and image generation, and integrating the results into Notion.

### 1.1. Contextual Data Loading
Upon invocation, `suggest_content.py` performs several crucial data loading steps to construct a rich context for the AI:

*   **Content Generation Guidelines (`src/prompts/content_generation_prompt.md`):** Loaded via `utils.general.read_file_content()`. This Markdown file contains the core instructions for the AI regarding the type, tone, and structure of social media content ideas. It defines the AI's persona, goals, content pillars, and format requirements. This is a primary control point for the AI's creative output.
*   **Social Media Best Practices (`src/prompts/social_media_best_practices.md`):** Loaded via `utils.general.read_file_content()`. This comprehensive Markdown document provides broader strategic context, including platform-specific best practices (Facebook, Instagram, Blogging), target audience insights, competitive positioning, and the desired "small town, expert feel." This guides the AI in generating content that is not only creative but also strategically aligned with business objectives.
*   **Machine Context Provider (MCP) (`src/data/machine_context.json`):** Loaded as a JSON object using `json.load()`. This file, populated by `src/utils/woocommerce_data_pull.py`, contains structured data about Rental Village's available and (potentially) unavailable machines, along with general business information. It is critical for ensuring factual accuracy and preventing the AI from generating content for non-existent or unavailable equipment. This acts as a dynamic, factual knowledge base for the AI.
*   **Existing Notion Ideas (`utils.notion_helpers.get_existing_notion_ideas()`):** This function queries the Notion database for previously generated content ideas (specifically their `Name` and `Copy` properties). The retrieved list of existing ideas serves as a negative constraint, instructing the AI to avoid generating repetitive or overly similar content. This provides a memory of past outputs to reduce redundancy.

### 1.2. AI Invocation and Notion Integration
After loading all contextual data, `suggest_content.py` proceeds to:

*   **Generate Content Ideas:** Calls `utils.gemini_helpers.generate_ideas_with_gemini()`, passing all loaded contextual data (guidelines, user input, existing ideas, MCP, social media best practices) as arguments. This is the primary AI text generation step.
*   **Process and Store Ideas:** Iterates through the JSON array of content ideas returned by `generate_ideas_with_gemini()`. For each idea, it calls `utils.notion_helpers.add_idea_to_notion()` to persist the idea and its associated generated images into the Notion database.

## 2. AI Model Interactions: `src/utils/gemini_helpers.py`

This module encapsulates all communication with the Google Gemini API for both text and image generation.

### 2.1. `generate_ideas_with_gemini(guidelines, num_ideas, user_input, existing_ideas, machine_context, social_media_best_practices)`
This function is responsible for crafting the comprehensive prompt for the Gemini text model and processing its response.

*   **Prompt Assembly:** A multi-part string `prompt` is dynamically constructed. This is where the layered guidance for the AI is most evident:
    *   **Role & Task Definition:** Initializes with a clear persona and task (`You are a creative social media manager... Your task is to generate {num_ideas} fresh, engaging content ideas.`).
    *   **Machine Context Integration:** If `machine_context` is provided, a detailed JSON representation of available machines and business info is injected. A critical directive (`You MUST only generate ideas for machines listed under 'available_machines'.`) is included to enforce factual constraints. This directly controls the AI's knowledge base regarding product availability.
    *   **Strategic Guidelines:** The content of `social_media_best_practices` is appended, providing high-level strategic direction for content tone, audience, and platform-specific nuances. This shapes the AI's understanding of brand voice and marketing goals.
    *   **Core Content Guidelines:** The content of `content_generation_prompt.md` (`guidelines`) is appended, detailing content pillars, tone, and required output format. This provides the specific rules for content creation.
    *   **User Input:** Any `user_input` provided by the user is included as inspiration, allowing for ad-hoc topic steering.
    *   **Repetition Avoidance:** If `existing_ideas` are present, they are formatted and appended with an explicit instruction to the AI to avoid generating similar content. This acts as a dynamic memory for the AI within the current generation session, preventing redundant suggestions.
    *   **Output Format Enforcement:** A strict JSON output format is specified, including an example, to ensure the model's response is machine-readable and consistent (`Return your response as a valid JSON array of objects...`). This is a crucial control for programmatic consumption of AI output.
*   **API Call:** The assembled `prompt` is sent to the `gemini-1.5-flash` model via `client.models.generate_content()`. This model is optimized for text generation tasks.
*   **Response Parsing:** The raw text response from the Gemini API is cleaned (removing markdown code block delimiters) and then parsed into a Python list of dictionaries using `json.loads()`. Robust error handling is implemented to catch API errors or invalid JSON responses.

### 2.2. `generate_image_with_gemini(prompt, output_path, num_images, instructions_path)`
This function handles the generation of images using the Gemini image model.

*   **Image Instructions Loading:** If `instructions_path` is provided (pointing to `src/prompts/image_generation_instructions.md`), its content is loaded via `utils.general.read_file_content()`. This provides general directives for image quality, authenticity, and composition, ensuring visual consistency.
*   **Image Prompt Construction:** The `full_prompt` for the image model is constructed by prepending the loaded `image_instructions` to the `prompt` argument (which itself is a concatenation of the content idea's `title`, `body`, and `keywords`). This ensures the image generation is guided by both general aesthetic/quality rules and specific content relevance, providing highly targeted visual output.
*   **API Call:** The `full_prompt` is sent to the `gemini-2.0-flash-preview-image-generation` model via `client.models.generate_content()`. This model is designed for text-to-image generation.
*   **Image Saving:** The binary image data returned by the API is processed using `PIL.Image` and `io.BytesIO`, and then saved as PNG files to the `generated_images/` directory. Multiple variations (`num_images`) can be generated and saved.

## 3. Notion Database Interactions: `src/utils/notion_helpers.py`

This module provides helper functions for interacting with the Notion API, primarily for reading existing data and writing new content ideas.

### 3.1. `get_existing_notion_ideas(notion, database_id)`

*   **Purpose:** Fetches existing content ideas (titles and copies) from the specified Notion database.
*   **Mechanism:** Queries the Notion database using `notion.databases.query()`, filtering for pages with non-empty `Name` (title) or `Copy` (rich_text) properties. It extracts the plain text content of these properties.
*   **Output:** Returns a list of dictionaries, each containing the `title` and `copy` of an existing Notion page. This output is crucial for the AI's repetition avoidance mechanism, acting as a dynamic memory of past content.

### 3.2. `add_idea_to_notion(notion, idea, generate_image_with_gemini, num_images)`

*   **Purpose:** Creates a new page in the Notion database for a generated content idea and uploads associated images.
*   **Mechanism:**
    *   Constructs a `properties` dictionary based on the `idea` (title, pillar, body, status, post date).
    *   Creates a new Notion page using `notion.pages.create()`.
    *   Calls the `generate_image_with_gemini` function (passed as an argument) to obtain local paths to generated images.
    *   Iterates through the generated image paths and calls `upload_image_to_notion()` for each image.

### 3.3. `upload_image_to_notion(page_id, image_path, property_name)`

*   **Purpose:** Uploads a local image file to a Notion database page's `files` property.
*   **Mechanism:** Utilizes Notion's direct file upload API. It first initiates an upload to get a `file_upload_id`, then sends the image binary data, and finally patches the Notion page to link the uploaded file to the specified `property_name` (e.g., "Creative"). This ensures that visual assets are correctly associated with their content ideas in Notion.

## 4. Data Preparation & Utility: `src/utils/woocommerce_data_pull.py` and `src/utils/general.py`

*   **`src/utils/woocommerce_data_pull.py`:** This standalone script is responsible for extracting product data from a WooCommerce store via its REST API. It fetches product categories and published products, then processes their `name`, `description`, `short_description`, `images`, `price`, `sku`, `categories`, and `tags`. It specifically maps WooCommerce product `tags` to `image_keywords` in the generated `machine_context.json`. This script is executed manually to update the MCP, serving as the bridge between WooCommerce and the AI's knowledge base.
*   **`src/utils/woocommerce_schema_inspector.py`:** A diagnostic utility to inspect the raw JSON schema of WooCommerce products. This is crucial for understanding the structure of product data and correctly mapping fields for the MCP.
*   **`src/utils/general.py`:** Contains the `read_file_content(file_path)` utility function, used across the application to safely read the content of Markdown prompt files. This promotes code reusability and simplifies file I/O.

## 5. AI Guidance and Control Mechanisms (Technical Deep Dive)

The application employs a sophisticated, multi-layered approach to guide and control the AI's output, ensuring relevance, accuracy, and adherence to brand guidelines:

*   **Layered Prompt Construction:** This is the most critical mechanism. The `generate_ideas_with_gemini` function dynamically builds a single, comprehensive prompt by concatenating multiple contextual inputs. This allows for a hierarchical influence on the AI's reasoning:
    1.  **High-Level Strategy:** `social_media_best_practices.md` sets the overall tone, audience, and competitive positioning.
    2.  **Core Content Rules:** `content_generation_prompt.md` defines the content pillars, required output format (JSON schema), and creative directives.
    3.  **Factual Constraints:** The `machine_context.json` (MCP) is injected as structured JSON data, coupled with explicit instructions (`You MUST only generate ideas for machines listed under 'available_machines'.`) to prevent factual errors and brand inconsistencies. This is a direct programmatic control over the AI's knowledge base, ensuring it operates within the bounds of available inventory.
    4.  **Repetition Avoidance:** `existing_ideas` from Notion are provided as negative examples, guiding the AI to generate novel content. This acts as a dynamic memory for the AI within the current generation session, preventing redundant suggestions.
    5.  **Specific Input:** `user_input` allows for ad-hoc guidance for particular content needs.
*   **Structured Output Enforcement:** By explicitly requesting a JSON array with predefined keys (`pillar`, `title`, `body`, `keywords`) and providing an example, the application forces the AI to return a machine-readable and predictable response, simplifying downstream processing. This reduces the need for complex parsing and validation logic.
*   **External Data Integration (MCP):** The `machine_context.json` acts as a curated, external knowledge base. This is a powerful control mechanism, as it allows for updating the AI's factual understanding of available products without retraining the model or modifying core prompt logic. The `woocommerce_data_pull.py` script ensures this data can be refreshed from the source of truth (WooCommerce), providing a scalable way to manage product information.
*   **Human-in-the-Loop Validation:** All AI-generated content is initially marked with "AI Suggestion" status in Notion. This mandates human review and approval before any content is published, serving as the ultimate quality gate and ensuring brand alignment and creative oversight. This is a crucial safety net for AI-generated content.
*   **Modular Prompt Management:** Storing different types of prompts in separate Markdown files (`.md`) within `src/prompts/` allows for easy, non-code-level adjustments to AI behavior. This promotes agility and enables content strategists to fine-tune AI output without developer intervention, fostering collaboration between technical and marketing teams.
*   **Image Prompt Specificity:** The image generation prompt combines general `image_generation_instructions.md` with specific `title`, `body`, and `keywords` from the generated content idea. This ensures highly relevant and targeted image outputs, improving the visual quality and relevance of generated assets.

## 6. Areas for Improvement

Based on a thorough review of the codebase and the current `docs/application_overview.md`, here are several potential areas for improvement:

*   **Automated MCP Refresh:** Implement a scheduled job (e.g., cron, cloud function, or a simple daily execution) to periodically execute `src/utils/woocommerce_data_pull.py` and update `src/data/machine_context.json`. This would ensure the MCP is always up-to-date with WooCommerce inventory without manual intervention, reducing the risk of outdated information.
    *   **Reasoning:** Currently, `woocommerce_data_pull.py` is a manual process. Automating this is crucial for maintaining data freshness and preventing the AI from generating content for unavailable machines, which was a primary concern.
*   **Enhanced Error Handling and Logging:** While basic `try-except` blocks are present, more granular error handling and comprehensive logging (e.g., using Python's `logging` module with different levels) would be beneficial. This includes detailed logging of API responses (especially errors), prompt construction, and AI model outputs for debugging and performance monitoring.
    *   **Reasoning:** Current error messages are sometimes generic. Better logging would provide clearer insights into failures, especially with external API calls (Gemini, Notion, WooCommerce) and JSON parsing issues.
*   **Asynchronous API Calls (Potential):** For scenarios involving a large `num_ideas` or multiple image variations, sequential API calls to Gemini and Notion could become a bottleneck. Investigating asynchronous programming (e.g., `asyncio` with `aiohttp` for HTTP requests) could improve performance.
    *   **Reasoning:** While not a critical issue for small-scale use, this could become a performance bottleneck as the application scales or if `num_images` is increased significantly.
*   **Prompt Versioning and Management:** As prompt files evolve, a simple versioning system (e.g., Git for the prompt files themselves, or a more sophisticated prompt management solution) could help track changes and revert if necessary. This is especially relevant as content strategists might directly edit these files.
    *   **Reasoning:** Currently, prompt files are plain Markdown. While easy to edit, tracking changes and ensuring consistency across different versions could become challenging without a formal versioning strategy.
*   **Dynamic Prompt Adjustment based on Feedback:** The "Human-in-the-Loop" is a strong control. However, there's no automated feedback loop from Notion (e.g., human edits, approval/rejection reasons) back into the AI's learning or prompt refinement process. This could involve analyzing approved content for patterns or using explicit human feedback to dynamically adjust prompt weights or parameters.
    *   **Reasoning:** This would move the system towards continuous improvement, allowing the AI to learn from human curation and reduce the need for manual prompt engineering over time.
*   **Image Generation Quality Control & Selection:** The current process generates `num_images` and uploads all. Implementing a mechanism for human selection of the best image(s) from the generated variations *before* Notion upload, or even an AI-driven pre-selection based on quality metrics, could improve efficiency.
    *   **Reasoning:** Generating multiple images is good, but selecting the best one is still a manual step. Automating or streamlining this could save time.
*   **Configuration Management:** While `.env` is used for secrets, other configuration parameters (e.g., default `num_ideas`, image output paths, Notion property names) are hardcoded or derived. Centralizing these in a configuration file (e.g., `config.ini`, `config.json`) could make the application more flexible and easier to manage.
    *   **Reasoning:** Hardcoded values can make maintenance difficult. A dedicated configuration file would improve flexibility.
*   **Unit Testing Expansion:** While `test_notion_helpers.py` exists, expanding unit tests to cover `gemini_helpers.py` (mocking API calls) and `suggest_content.py` (mocking file reads and Notion/Gemini interactions) would significantly improve code quality and prevent regressions.
    *   **Reasoning:** Comprehensive testing is crucial for ensuring the reliability of the application, especially as new features are added.

This detailed overview provides a solid foundation for understanding the application's current architecture and serves as a springboard for targeted future enhancements.