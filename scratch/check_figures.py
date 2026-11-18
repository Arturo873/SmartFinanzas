import docx

doc = docx.Document("docs/Manual_de_Usuario_SmartFinanzas.docx")
fig_caps = [p.text for p in doc.paragraphs if p.text.startswith("Figura")]
print(f"Total Figures Found: {len(fig_caps)}")
for f in fig_caps:
    print(" *", f)
