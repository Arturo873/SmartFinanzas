import docx

doc = docx.Document("docs/Terminos_y_Condiciones_SmartFinanzas.docx")
print("Total Paragraphs:", len(doc.paragraphs))
print("Total Tables:", len(doc.tables))
print("Total Sections:", len(doc.sections))

headings = [p.text for p in doc.paragraphs if p.text.startswith("Título") or p.text.startswith("Índice")]
print("Key Headings found:")
for h in headings:
    print(" -", h)
