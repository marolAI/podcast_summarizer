
import os
import json
import time
import modal
import streamlit as st


def add_space(num_spaces=1):
    for _ in range(num_spaces):
        st.write("\n")
        

def process_podcast_info(url):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call(url, '/content/podcast/')
    return output


def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info['podcast_details']['podcast_title']
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info

    return data_dict


def main():
    st.title("Newsletter Dashboard")

    available_podcast_info = create_dict_from_json_files('./sample_podcasts')

    with st.sidebar:
        #Input fields
        st.header("Podcast RSS Feeds")
        st.markdown(
            """Podcast Summarizer is an app that condenses lengthy podcast episodes into concise, 
            informative summaries using AI, making it easy to grasp the key insights on-the-go."""
        )

        add_space()
        
        # Dropdown box
        st.subheader("Available Podcasts Feeds")
        selected_podcast = st.selectbox("Select Podcast", options=available_podcast_info.keys())
        
        add_space()
        
        # User Input box
        st.subheader("Add and Process New Podcast Feed")
        url = st.text_input("Link to RSS Feed")

        process_button = st.button("Process Podcast Feed")
        # st.markdown("**Note**: Podcast processing can take upto 5 mins, please be patient.")
    
    placeholder = st.empty()
    
    if selected_podcast:
        with placeholder.container():
            podcast_info = available_podcast_info[selected_podcast]
            
            # Newsletter content
            col1, col2 = st.columns([2, 8])
            
            with col1:
                st.image(podcast_info['podcast_details']['episode_image'], width=100)
                
            with col2:
                st.write("**Episode Title:**", podcast_info['podcast_details']['episode_title'])
                st.write("**Guest:**", podcast_info['podcast_guest']['guest_name'])
                
            # Display the five key moments
            st.subheader("Key Moments")
            key_moments = podcast_info['podcast_highlights']
            for moment in key_moments.split('\n'):
                st.markdown(
                    f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)
                
            # Display the podcast episode summary
            st.subheader("Summary")
            st.write(podcast_info['podcast_summary'])
            
            st.subheader("Guest Details")
            st.write(podcast_info["podcast_guest"]['summary'])

    if process_button:
        with placeholder.container():
            with st.spinner("Processing podcast episode..."):
                podcast_info = process_podcast_info(url)
                time.sleep(5)

        with placeholder.container():
            # Newsletter content
            col1, col2 = st.columns([2, 8])
            
            with col1:
                st.image(podcast_info['podcast_details']['episode_image'], width=100)
                
            with col2:
                st.write("**Episode Title:**", podcast_info['podcast_details']['episode_title'])
                st.write("**Guest:**", podcast_info['podcast_guest']['guest_name'])
                
            # Display the five key moments
            st.subheader("Key Moments")
            key_moments = podcast_info['podcast_highlights']
            for moment in key_moments.split('\n'):
                st.markdown(
                    f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)
                
            # Display the podcast episode summary
            st.subheader("Summary")
            st.write(podcast_info['podcast_summary'])
            
            st.subheader("Guest Details")
            st.write(podcast_info["podcast_guest"]['summary'])


if __name__ == '__main__':
    main()
