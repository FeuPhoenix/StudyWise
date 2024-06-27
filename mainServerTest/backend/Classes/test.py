from spire.presentation import *
from spire.presentation.common import *

# Create a Presentation object
presentation = Presentation()
# Load a PowerPoint presentation in PPTX format
presentation.LoadFromFile("D:/COLLEGE/StudyWise/mainServerTest/assets/input_files/text-based/decision analysis.pptx")
# Or load a PowerPoint presentation in PPT format
#presentation.LoadFromFile("Sample.ppt")

# Convert the presentation to PDF format
presentation.SaveToFile("D:/COLLEGE/StudyWise/mainServerTest/assets/input_files/text-based/decision analysis.pdf", FileFormat.PDF)
presentation.Dispose()
# from spire.doc import *
# from spire.doc.common import *
        
# # Create a Document object
# document = Document()
# # Load a Word DOCX file
# document.LoadFromFile("Sample.docx")
# # Or load a Word DOC file
# #document.LoadFromFile("Sample.doc")

# # Save the file to a PDF file
# document.SaveToFile("WordToPdf.pdf", FileFormat.PDF)
# document.Close()