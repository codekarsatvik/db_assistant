import gradio as gr
from database_assistant.crew import DatabaseAssistant

def run_db_assistant(user_query):
    # Prepare input dict for the crew
    inputs = {"user_query": user_query}
    try:
        # Run the crew with the user query as input
        result = DatabaseAssistant().crew().kickoff(inputs=inputs)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def main():
    with gr.Blocks() as demo:
        gr.Markdown("# Database Assistant (CrewAI)")
        chatbot = gr.Chatbot()
        with gr.Row():
            user_input = gr.Textbox(label="Ask a database question...", placeholder="e.g. Show me all users who signed up last week")
            send_btn = gr.Button("Send")
        def respond(message, history):
            response = run_db_assistant(message)
            history = history or []
            history.append((message, response))
            return "", history
        send_btn.click(respond, [user_input, chatbot], [user_input, chatbot])
        user_input.submit(respond, [user_input, chatbot], [user_input, chatbot])
    demo.launch()

if __name__ == "__main__":
    main() 