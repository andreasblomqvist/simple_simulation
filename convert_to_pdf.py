import markdown
import pdfkit
import os

def convert_md_to_pdf(md_file, pdf_file):
    # Read the markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Add some basic styling
    styled_html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                h3 {{ color: #7f8c8d; }}
                code {{ background-color: #f8f9fa; padding: 2px 4px; border-radius: 4px; }}
                pre {{ background-color: #f8f9fa; padding: 15px; border-radius: 4px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f8f9fa; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
    </html>
    """
    
    # Convert HTML to PDF
    pdfkit.from_string(styled_html, pdf_file)

if __name__ == "__main__":
    # Ensure the docs directory exists
    os.makedirs('docs', exist_ok=True)
    
    # Convert the file
    convert_md_to_pdf('docs/simulation_engine.md', 'docs/simulation_engine.pdf')
    print("PDF has been generated successfully!") 