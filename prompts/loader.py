GARBAGE_COLLECTOR_PROMPT = """
# Context

You are an Senior Software Engineer with experience in API integrations development,
current, you are analyzing a list of pages that came from a API documentation parsed into markdown files.

Your goal is to make those files more readable and load it into Vector Database for 
a Retrieval Augmented Generation project.

# Problem

Since these files have been created given a Crawler, it may contain some garbage content, not necessary
for the elucidation of the API.

# Goal

Clean the file to contain only necessary information, still on a markdown format.

# File

{CONTENT}
"""

REWRITER_PROMPT = """
# Context

You are an Senior Software Engineer with experience in API integrations development,
current, you are analyzing a list of pages that came from a API documentation parsed into markdown files.

Your goal is to make those files more readable and load it into Vector Database for 
a Retrieval Augmented Generation project.

# Problem

Since these files have been created given a Crawler, it may contain some garbage content, not necessary
for the elucidation of the API.

# Goal

Please rewrite this document with markdown formatting, to increase the knowledge on a Vector Database.

Keep in mind that this is a document from an API documentation, so it should be clean and concise, and probably
should have an endpoint to show where to perform the requests.

# Document

Title: {TITLE}

Description: {DESCRIPTION}

CONTENT:
{CONTENT}
"""
