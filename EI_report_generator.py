import os
import subprocess
import base64
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from genaicore import azure_openai_text_embeddings_llm, azure_gpt4_openai_text_chat_llm
from docx2pdf import convert
from langchain.text_splitter import CharacterTextSplitter
# Global definitions
embeddings = azure_openai_text_embeddings_llm
# text_splitter = CharacterTextSplitter(
#     separator="\n", chunk_size=1000, chunk_overlap=150, length_function=len
# )
text_splitter = SemanticChunker(embeddings)

standards="""
| Parameter | 24-hour Standard | Annual Standard |
|-----------|------------------|-----------------|
| PM10      | 50 µg/m³         | 25 µg/m³        |
| PM2.5     | 25 µg/m³         | 8 µg/m³         |
| TSP       |     -            | 90 µg/m³        |"""

query_sensitive_receptors ='''Retrieve receptor locations along with 
Extract the following predicted concentrations and deposition levels:
- Predicted Annual Average TSP Concentrations
- Predicted Annual Average PM10 Concentrations
- Predicted Annual Average PM2.5 Concentrations
- Predicted Annual Average Dust Deposition Levels
- Maximum predicted 24-Hour Average PM10 concentrations
- Maximum predicted 24-Hour Average PM2.5 concentrations'''

# template_sensitive_receptors = """You are an AI environmental analyst. Your task is to analyze the retrieved environmental data and present it in a structured format. The response should be written in **Markdown** format.

# ---

# ### **Context: Retrieved Environmental Data**  
# {context}

# ### **Environmental Standards**  
# {standards}

# ---

# ### **Instructions for Data Analysis**  
# 1. For **annual values**, consider only the **cumulative** values.  
# 2. For **24-hour values**, take only the **worst-case values**.  
# 3. Extract the values for **PM10, PM2.5, and TSP** from the provided context.  
# 4. Compare the extracted values against the given environmental standards.  
# 5. Use the following rules for marking compliance for Meets:  
#     - If **all parameter values** are **less than** the standard, mark it as **"Yes"** (✅).  
#     - If **any single parameter value** is **equal to** or **greater than** the standard, mark it as **"No"** (❌).  
# 6. In the **Observations** column:  
#     - Observation on the paramters and standards in short  
#     - Mention the parameters that **exceed** the standards.  
#     - Highlight parameters that are **close to the standards or equal** (difference of 1-2 units) and could become problematic.  

# ---

# ### **Output Format**  
# The output must follow the exact structure below and be written in **Markdown** format:

# # **[Extracted Company Name] - Environmental Impact Assessment**  

# ### **Criteria Applied Metrics**  

# | Parameter | 24-hour Standard | Annual Standard |
# |-----------|------------------|-----------------|
# | PM10      | 50 µg/m³         | 25 µg/m³        |
# | PM2.5     | 25 µg/m³         | 8 µg/m³         |
# | TSP       | -                | 90 µg/m³        |

# ---

# ### **Impact Assessment Criteria Applied**  

# | Receptors           |              PM10          |              PM2.5           |    TSP     |       |                                     |   
# |                     |     24-hour  |  Annual     |  24-hour      |  Annual      |  Annual    | Meets |        Observation                  |
# |---------------------|--------------|-------------|---------------|--------------|------------|-------|-------------------------------------|
# | R1                  | Value        | Value       | Value         | Value        | Value      |       | High cumulative PM2.5               |
# | R2                  | Value        | Value       | Value         | Value        | Value      |       | Exceeds PM10 criteria cumulatively  |
# ...
# ---
# """
template_sensitive_receptors = """
You are an AI environmental analyst. Your task is to analyze the retrieved environmental data and present it in a structured format. The response should be written in **Markdown** format.

---

### **Context: Retrieved Environmental Data**  
{context}

### **Environmental Standards**  
{standards}

---

### **Instructions for Data Analysis**  
- For **annual values**, consider only the **cumulative** values.  
- For **24-hour values**, take only the **worst-case values**.  
- Extract the values for **PM10, PM2.5, and TSP** from the provided context.  
- Compare the extracted values against the given environmental standards.  
- If the all the  parameters value is **less than** the standard, mark it as **"Yes"** (✅).  
- If the any single parameter value is **equal  ** the standard, mark it as **"No"** (❌).  
- If the any single parameter value is **greater than ** the standard, mark it as **"No"** (❌).  
- In the **Observations** column, write short observation on the parameter values and mention the parameters that exceed the standards at each receptor and short observation of the which parameter are close(diference is 1-5) to standards and going to be problematic

---
output format exatcly like this and should be written in **Markdown** format. - 

## **Report Heading**  
**[Extracted Company Name] - Environmental Impact Assessment**  

### **Criteria Applied Metrics**  

| Parameter | 24-hour Standard | Annual Standard |
|-----------|------------------|-----------------|
| PM10      | 50 µg/m³         | 25 µg/m³        |
| PM2.5     | 25 µg/m³         | 8 µg/m³         |
| TSP       | -                | 90 µg/m³        |

---

### **Impact Assessment Criteria Applied**  
| Receptors | PM10 (24-hour) | PM10 (Annual) | PM2.5 (24-hour) | PM2.5 (Annual) | TSP (Annual) | Meets Standards? | Observation |
|-----------|----------------|---------------|-----------------|----------------|--------------|------------------|-------------|
| R1        | Value          | Value         | Value           | Value          | Value        | ✅ Yes           | High cumulative PM2.5 |
| R2        | Value          | Value         | Value           | Value          | Value        | ❌ No            | Exceeds PM10 criteria cumulatively |
|    ...    |   ...          |  ...          |   ...            |  ...          |  ...          |       ...        |           ...           |

### **Conclusion**  
Summarize the findings, highlighting any exceedances or concerns.
"""
prompt = """
check the report provided in the Impact Assessment Criteria Applied table check the Meets dont change any values only you want to chnage meets
Use the following rules for marking compliance for Meets:  
    - If **all parameter values** are **less than** the standard, mark it as **"Yes"** (✅).  
    - If **any single parameter value** is **equal to** or **greater than** the standard, mark it as **"No"** (❌).  
In the **Observations** column:  
    - Observation on the paramters and standards in short
    - Mention the parameters that **exceed** the standards.  
    - Highlight parameters that are **close to the standards or equal** (difference of 1-2 units) and could become problematic.  
{report}


after all this after editiong the mistakes give me the exact markdow format after updated dont provide extra text or explanation other than the text in the report
"""

def save_markdown_to_file(documentation: str, file_path: str):
     with open(file_path, 'w', encoding='utf-8') as file:
          file.write(documentation)
     print(f"Markdown content has been saved to {file_path}")

def convert_md_to_docx(md_file: str, docx_file: str, template_file: str = None):
     try:
          command = ["pandoc", md_file, "-o", docx_file]
          if template_file:
                command.extend(["--reference-doc", template_file])
          subprocess.run(command, check=True)
          print(f"Successfully converted {md_file} to {docx_file}")
     except subprocess.CalledProcessError as e:
          print(f"Error during conversion: {e}")

def generate_air_quality_report(pdf_filepath: str, output_name: str = "Air Quality Report") -> str:
     """
     Generate an air quality assessment report from a PDF file and return it as a base64 string.
     Args:
          pdf_filepath (str): Path to the input PDF file containing air quality data.
          output_name (str): Base name for output files (without extension).
     Returns:
          str: Base64 encoded PDF content.
     """
     try:
          # Load and process the PDF
          loader = PyMuPDFLoader(pdf_filepath)
          pages = loader.load()
          
          # Split into chunks using the semantic chunker
          docs = text_splitter.split_documents(pages)
          
          # Clean the documents
          for doc in docs:
                doc.page_content = doc.page_content.replace("\n", "")
          
          # Create vector database and retriever
          db = FAISS.from_documents(docs, embeddings)
          retriever = db.as_retriever(search_kwargs={"k":20, "search_type": "mmr","semantic_search": True})
          
          # Get relevant information
          retrieved_docs = retriever.invoke(query_sensitive_receptors)
          retrieved_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
          
          # Generate initial report using the structured prompt
          prompt_template = ChatPromptTemplate.from_template(template_sensitive_receptors)
          formatted_prompt = prompt_template.invoke({
                "context": retrieved_text, 
                "standards": standards
          })
          response = azure_gpt4_openai_text_chat_llm.invoke(formatted_prompt)
          parsed_response = StrOutputParser().invoke(response)
          
          # Verify and update the report using the review prompt
          review_template = ChatPromptTemplate.from_template(prompt)
          review_prompt = review_template.invoke({"report": parsed_response})
          response_review = azure_gpt4_openai_text_chat_llm.invoke(review_prompt)
          final_report = StrOutputParser().invoke(response_review)
          
          # Save and convert files
          md_path = f"{output_name}.md"
          docx_path = f"{output_name}.docx"
          pdf_path = f"{output_name}.pdf"
          
          save_markdown_to_file(final_report, md_path)
          convert_md_to_docx(md_path, docx_path)
          convert(docx_path, pdf_path)
          
          # Read and encode PDF as base64
          with open(pdf_path, "rb") as pdf_file:
                encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
          
          # Clean up temporary files
          os.remove(md_path)
          os.remove(docx_path)
          os.remove(pdf_path)
          
          return encoded_pdf
          
     except Exception as e:
          print(f"Error generating report: {str(e)}")
          return None

# Example usage:
if __name__ == "__main__":
    pdf_file_path = "Att 5. Air Quality Assessment 4567 Old Northern Road Maroota.pdf"
    base64_pdf = generate_air_quality_report(pdf_file_path)
    if base64_pdf:
        print("Report generated successfully and encoded in base64.")
        with open("output_report_Eia_1.pdf", "wb") as pdf_file:
            pdf_file.write(base64.b64decode(base64_pdf))
        print("Base64 content has been converted to PDF and saved as output_report.pdf")