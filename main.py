import streamlit as st 
import pandas as pd 
# import plotly.express as px 
import os
from anthropic import Anthropic
from fpdf import FPDF

st.set_page_config(layout="wide")

OUTPUT_DIR = 'reports/'
os.environ["ANTHROPIC_API_KEY"] = #KEY
model = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

def call_claude_api(prompt):
    response = model.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response

def generate_response(prompt):
    response = model.messages.create(
      model="claude-3-opus-20240229",
      max_tokens=1024,
      messages=[
          {"role": "user", "content": df.to_csv(index=False)},
          {"role": "assistant", "content": prompt}
      ],
      temperature=0.0
    )
    return response.content[0].text

def download_report(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    # output_text = "\n".join(content)
    encoded_content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=encoded_content)
    path = os.path.join(OUTPUT_DIR, 'generated_report.pdf')
    pdf.output(path)
    

# st.markdown(
#     """
#     <style>
#     .css-1aumxhk {
#         max-width: 800px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

st.title('LLM Report Analysis')

left_column, right_column = st.columns(2)

with left_column:
    st.title('Upload CSV')
    uploaded_file = st.file_uploader('Choose a CSV file', type='csv')
    if uploaded_file:
        st.markdown('---')
        df = pd.read_csv(uploaded_file)
        st.write(df)
    
        row_number = st.number_input("Enter pattern row number:", min_value=0, max_value=len(df)-1, step=1)

        if st.button("Run"):
            if row_number is not None:
                if 0 <= row_number < len(df):

                    selected_row = df.iloc[row_number]
                    text = "We have a set of US counties for which we have determined three risk factors: " + selected_row['description'] + ". What might be the connection of these to high opioid death rate? Are there any related factors?"
                    
                    response = call_claude_api(text)
                    
                    st.write(response.content[0].text)
                else:
                    st.write("Row number out of range.")
            else:
                st.write("Please enter a row number.")


with right_column:
    st.title('Ask LLM')
    # prompt_input = st.chat_input("Enter your prompt here")

    # if st.button("Send"):
    # if prompt_input := st.chat_input("Enter your prompt here"):
    #     if prompt_input:
    #         response = generate_response(prompt_input)
    #         st.write(response)
            # downloadButton = st.button('Download')
            # if(downloadButton):
            #     download_report(response.content[0].text)
            # st.download_button(label='Download PDF',
            #         data=response.content[0].text.encode('latin-1', 'replace').decode('latin-1'),
            #         file_name='LLM_Report.pdf',
            #         mime='application/octet-stream'
            #         )
        # else:
        #     st.write("Please enter a prompt.")


    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Chat with Claude..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = generate_response(prompt)
            st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})