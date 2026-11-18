import docx

doc = docx.Document("docs/Manual_de_Usuario_SmartFinanzas.docx")
print("Total Paragraphs:", len(doc.paragraphs))
print("Total Tables:", len(doc.tables))
print("Total Sections:", len(doc.sections))

headings = [p.text for p in doc.paragraphs if p.text.startswith("Capítulo") or p.text.startswith("Control") or p.text.startswith("Índice")]
print("Key Headings found:")
for h in headings:
    print(" -", h)

total_images = sum(1 for p in doc.paragraphs for r in p.runs if 'drawing' in r._r.xml)
print("Total Embedded Drawings/Images:", total_images)
