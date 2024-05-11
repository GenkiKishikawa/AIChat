import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.callbacks.manager import get_openai_callback
from langchain.chains.summarize import load_summarize_chain

import validators


def init_page():
  st.set_page_config(
    page_title="Youtube Summarizer",
    page_icon="🤗"
  )
  st.header("Youtube Summarizer 🤗")
  st.sidebar.header("Options")

def init_messages():
  st.session_state.costs = []

def select_model():
  model = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
  if model == "GPT-3.5":
    model_name = "gpt-3.5-turbo"
  else:
    model_name = "gpt-4"
  
  return ChatOpenAI(model_name=model_name, temperature=0)

def get_url():
  url = st.text_input("URL: ", key="input")
  return url

def validate_url(url):
  pass

def get_document(url):
  with st.spinner("Fetching Content ..."):
    loader = YoutubeLoader.from_youtube_url(
      youtube_url=url,
      add_video_info=True,
      language=['en', 'ja']
    )
    return loader.load()

def summarize(llm, docs):
  prompt_template = """Write a concise Japanese summary of the following transcript of Youtube Video.
  
  {text}
  
  ここから日本語で書いてね。必ず3段落以内の200文字以内で簡潔にまとめること:
  """
  
  PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
  
  with get_openai_callback() as cb:
    chain = load_summarize_chain(
      llm,
      chain_type="stuff",
      verbose=True,
      prompt=PROMPT,
    )
    response = chain({"input_documents": docs})
  
  return response['output_text'], cb.total_cost


def main():
  init_page()
  llm = select_model()
  init_messages()
  
  container = st.container()
  response_container = st.container()
  
  with container:
    url = get_url()
    if not validators.url(url):
      st.write("Please enter a valid URL")
      output_text = None
    else:  
      document = get_document(url)
      if document:
        with st.spinner("ChatGPT is typing ..."):
          output_text, cost = summarize(llm, document)
        st.session_state.costs.append(cost)
      else:
        output_text = None
  
  with response_container:
    if output_text:
      st.markdown("## Summary")
      st.write(output_text)
      st.markdown("-----------------------")
      st.write(document)
      
  costs = st.session_state.get('costs', [])
  st.sidebar.markdown("## Costs")
  st.sidebar.markdown(f"**Total cost: ${sum(costs):.5f}**")
  for cost in costs:
      st.sidebar.markdown(f"- ${cost:.5f}")

if __name__ == "__main__":
  main()