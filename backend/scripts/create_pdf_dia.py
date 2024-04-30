# -*- coding: utf-8 -*-


import jinja2
import pdfkit


# pdfkit is just a wrapper for whktmltopdf. you need to install wkhtml and have it on the path
# alternatively, you can move wkhtmltoimage.exe, wkhtmltopdf.exe and wkhtmltox.dll into the working directory

# Create some data






# Load the template
env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
template = env.get_template("dia_template.html")
# pass df, title, message to the template.
poll = {'Poll_data': None, 'head_text': 'Тестова Шапка голосування', 'ФормаГолос': 'Опитування', 'Data': '', 'ВопросГолосования': 'Тестове голосуванн я', 'РезультатГолосования': [{'имя': 'За', 'варианты': 3, 'проценты': 42.857142857142854}, {'имя': 'Против', 'варианты': 3, 'проценты': 42.857142857142854}, {'имя': 'Воздержался', 'варианты': 1, 'проценты': 14.285714285714285}]}




html_out = template.render(head_text=poll['head_text'],
                           question=poll['ВопросГолосования'],
                            results=poll['РезультатГолосования'],
                           user_name='Name',
                            user_answer='Da'
                           )
options = {
  "enable-local-file-access": None
}

# write the html to file
with open("output2.html", 'wb') as file_:
    file_.write(html_out.encode("utf-8"))

# write the pdf to file
pdfkit.from_string(html_out, output_path="output.pdf", css=["template.css"], options=options)
