def give_paragraph_analysis(paragraph,classifier):
   
  res = classifier(paragraph)
  return res