# Smart Fashion Search Assistant: Understanding You Beyond Keywords

## Problem Statement

E-commerce search engines are built for **literal** queries.

When a user types something like:
> "I need a formal top for my beige pants"

The system often misinterprets it and returns:
> Beige formal tops ❌ (literal keyword match)

But the **user's actual intent** might be:
> "Show me tops that *contrast* well with beige pants, suitable for a formal setting" ✅

There is a clear **disconnect between natural, indirect queries** and how search engines interpret them.

## Project Overview

The aim is to build a **semantic, intelligent search interface** for fashion e-commerce platforms that:
1. Understands **indirect, natural language queries**
2. Transforms them into **precise, intent-aware search queries**
3. Uses a **chatbot-style assistant** to guide users through refinements based on product metadata and reviews

## Core Idea

Instead of keyword-based matching, this assistant takes a **user-centric approach**:
- Detects **intent and context** (e.g., color coordination, occasion, material sensitivity)
- Reformulates the query into something that would actually yield **visually and stylistically relevant products**
- Offers **follow-up questions** to refine the search, based on:
  - Metadata (e.g., fabric, fit, sleeve length)
  - Reviews (e.g., "sleeves run long", "material is see-through")

## Example: From Query to Conversion

### Input Query (User):
> "I need a formal top for my beige pants"

### Step 1: LLM Interpretation
- Detects beige is a neutral color
- Suggests **contrasting formal colors** (e.g., navy, maroon, black)
- Adds filters for **"formal occasion"**, **"women's tops"**

**Transformed Search Query:**
> "Women's formal tops in navy, maroon, black — suitable for office wear"

---

### Step 2: Product Matching

Show:
- Structured cards for suitable tops
- Option to engage the assistant further

---

### Step 3: Follow-up Assistant

Bot:  
> "Many customers mentioned this top has slightly longer sleeves — would that work for you?"

Bot:  
> "Would you prefer sleeveless or 3/4th sleeves for a formal setting?"

User selects → Results refined dynamically

---

## Why This Matters

- Shoppers often **don't know the exact words** to use
- Fashion is **subjective** and **contextual** (color theory, body shape, trends)
- Indirect queries and visual goals are common in fashion shopping:
  - “Something that goes well with high-waisted jeans”
  - “A jacket that doesn’t look too bulky”
  - “A skirt like what Zendaya wore at the Oscars”

Current search engines cannot decode these nuances.

---

## Prototype Plan

1. **Input Handling:** Natural language queries from users
2. **LLM Layer:** Interpret query → detect intent → rewrite for search
3. **Catalog Search:** Use keyword and vector-based filtering over product data
4. **Follow-up Assistant:** Engage users using metadata, tags, and reviews
5. **UI Layer:** Streamlit or web app with search + chat interface

---

## Dataset Strategy

To prototype:
- Use a small **curated product CSV** of ~50 items with:
  - Name, category, color, fit, material, reviews
- Optionally test with **public fashion datasets** (Amazon, Rakuten)
- Hardcode or simulate metadata + reviews to mimic real-world conditions

