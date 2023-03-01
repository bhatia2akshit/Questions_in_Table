import streamlit as st
import pandas as pd
from streamlit_chat import message
from transformers import AutoTokenizer, TapasForQuestionAnswering


### model loading
tokenizer = AutoTokenizer.from_pretrained("./tapas_large_2")
model = TapasForQuestionAnswering.from_pretrained("./tapas_large_2")
loaded_table = ''

### response creation
def create_response(table, query) -> list:

    inputs = tokenizer(table=table, queries=query, truncation=True, padding="max_length", return_tensors="pt")
    outputs = model(**inputs)

    predicted_answer_coordinates, predicted_aggregation_indices = tokenizer.convert_logits_to_predictions(
        inputs,
        outputs.logits.detach(),
        outputs.logits_aggregation.detach()
    )

    answers = []
    for coordinates in predicted_answer_coordinates:
        for coordinate in coordinates:
            if not answers.__contains__(table.iat[coordinate]):
                answers.append(table.iat[coordinate])
    return answers


### response by chatbot
def chatbot_response(question, loaded_table):
    message('looking into dataset to find your answers.')
    response_list = []

    sub_table = loaded_table.astype(str)
    sub_table = sub_table.fillna('None')

    try:
        response = create_response(query=question,table=sub_table)

    except:
        message('Some error encountered. My apologies!')
        return

    if len(response) == 1 and response[0] == 'None':
        message('No Information is found from the file uploaded.')

    else:
        for res in response:

            if not response_list.__contains__(res):

                response_list.append(res)

    return response_list



### data loading
def load_data(file):
    message('starting the loading of the file.',is_user=False)
    df = pd.read_excel(file)
    length = len(df)
    if length == 0:
        message('no file is loaded')
        return

    else:
        loaded_table = df
    message('file is loaded')
    return loaded_table

st.header("TabularChat")

### chatbot screens
tab_setup, tab_chatbot = st.tabs(["setup", "chatbot"])
with tab_setup:
    st.header("chatbot_settings!")
    uploaded_file = st.file_uploader("Choose a file", type='.xlsx', )
    if st.button('load the file'):
        if uploaded_file is None:
            message('upload a file first')
        else:
            loaded_data = load_data(uploaded_file)
            columns_list = list(loaded_data.columns)
            st.session_state['data'] = loaded_data
            st.session_state['columns'] = columns_list



with tab_chatbot:

    if not st.session_state.__contains__('data'):
        st.header('Please upload the excel file first')
    else:
        column_container = st.container()
        input_container = st.container()
        message_container = st.container()

        with column_container:
            st.subheader('Columns Selection')
            if not st.session_state.__contains__('columns'):
                columns = ['waiting for the file to be loaded :D']
            else:
                columns = st.session_state['columns']
            columns_selected = st.multiselect('Which column do you want to use?', columns)
            st.session_state['selected'] = columns_selected

        with input_container:
            st.subheader('Chatbot')
            input_ = st.text_input('chat with bot')
            st.session_state['input'] = input_

        with message_container:
            message(input_, is_user=True)
            if st.button('start search'):
                try:
                    loaded_data = st.session_state['data']
                    if st.session_state.__contains__('selected'):
                        loaded_data = loaded_data[st.session_state['selected']]
                    input_ = st.session_state['input']
                    response_list = chatbot_response(question=input_,loaded_table=loaded_data)
                    output = ''
                    for index, response in enumerate(response_list):
                        output += f'{index+1}. {response} \n'
                    message('This is what I found.')
                    message(output)
                except:
                    message('Some error occurred.')
                    pass