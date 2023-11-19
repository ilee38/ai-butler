from time import sleep
import openai
import os

FILES_PATH = "./data_files"

client = openai.OpenAI(
   api_key=os.environ.get("OPENAI_API_KEY")
)

def upload_files(path):
   """ Upload the files from which the Assistant will retrieve information from.
   """
   files_to_upload = []
   openai_file_ids = []

   if not os.path.exists(path):
      print(f"Error: file path {path} does not exists.")
      exit(1)

   # Upload all .md files from the directory
   for filename in os.listdir(path):
      if filename.endswith(".md"):
         file_path = os.path.join(path, filename)
         files_to_upload.append(file_path)

   print("Uploading files...")
   for f in files_to_upload:
      file = client.files.create(
         file=open(f, "rb"),
         purpose="assistants"
      )
      openai_file_ids.append(file.id)
      sleep(0.5)
   print("Done.")

   return openai_file_ids


def create_assistant(openai_file_ids):
   """ Creates an Assistant with the given file ids.
   """
   return client.beta.assistants.create(
      name="AI butler",
      instructions="You are a personal assistant that can search and retrieve information from files. Look for information in the files given to you to answer questions.",
      tools=[{"type": "retrieval"}],
      model="gpt-3.5-turbo-1106",
      file_ids=openai_file_ids
   )


def poll_run_status(thread, run):
   return client.beta.threads.runs.retrieve(
      thread_id=thread.id,
      run_id=run.id
   ).status


def clear_the_screen():
   if os.name == "nt":
      _ = os.system("cls")
   else:
      _ = os.system("clear")


def print_response(messages):
   """ Prints the Assistant's response.
       The messages param is expected to be the thread's messages list sorted in
       descending order (sorted by the created_at timestamp of the messages).
   """
   print(f"\n[AI butler]: {messages[0].content[0].text.value}\n")


def start_thread(assistant):
   thread = client.beta.threads.create()

   clear_the_screen()
   print("""
   ================================================================================
         Welcome, I'm your AI butler. Ask me anything about the STEM hash blog.
         (Enter 'q' to exit.)
   ================================================================================
         """)

   while True:
      # Get message from user
      msg = input()

      if msg.lower() == "q":
         break

      message = client.beta.threads.messages.create(
         thread_id=thread.id,
         content=msg,
         role="user"
      )

      run = client.beta.threads.runs.create(
         thread_id=thread.id,
         assistant_id=assistant.id,
      )

      run_status = poll_run_status(thread, run)
      while run_status != "completed":
         sleep(0.5)
         run_status = poll_run_status(thread, run)

      # Retrieve message list, sorted in descending order by default
      messages = client.beta.threads.messages.list(
         thread_id=thread.id
      ).data

      print_response(messages)


def main():
   openai_file_ids = upload_files(FILES_PATH)
   assistant = create_assistant(openai_file_ids)
   start_thread(assistant)


if __name__ == "__main__":
   main()
