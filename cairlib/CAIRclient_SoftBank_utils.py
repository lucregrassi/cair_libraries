from cairlib.DialogueStatistics import DialogueStatistics
from cairlib.SpeakerInfo import SpeakerInfo
import requests
import json
import time
import socket
import string


class Utils(object):
    def __init__(self, logger, app_name, language, server_ip, registration_ip):
        super(Utils, self).__init__()
        self.logger = logger
        self.language = language
        self.server_ip = server_ip
        self.registration_ip = registration_ip
        self.al = ALProxy("ALAutonomousLife")
        self.memory = ALProxy("ALMemory")
        self.animated_speech = ALProxy("ALAnimatedSpeech")
        self.configuration = {"bodyLanguageMode": "contextual"}
        self.dialogue_state_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                        "/dialogue_state.json"
        self.speakers_info_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                       "/speakers_info.json"
        self.dialogue_statistics_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                             "/dialogue_statistics.json"

        try:
            # self.voice_speed = "\\RSPD=100\\"
            self.voice_speed = "\\RSPD=" + str(self.memory.getData("CAIR/voice_speed")) + "\\"
        except:
            self.memory.insertData("CAIR/voice_speed", 80)
            self.voice_speed = "\\RSPD=80\\"

    def setAutonomousAbilities(self, blinking, background, awareness, listening, speaking):
        self.al.setAutonomousAbilityEnabled("AutonomousBlinking", blinking)
        self.al.setAutonomousAbilityEnabled("BackgroundMovement", background)
        self.al.setAutonomousAbilityEnabled("BasicAwareness", awareness)
        self.al.setAutonomousAbilityEnabled("ListeningMovement", listening)
        self.al.setAutonomousAbilityEnabled("SpeakingMovement", speaking)

    def compose_sentence(self, sentence_pieces):
        sentence = ""
        # print(sentence_pieces)
        for elem in sentence_pieces:
            if sentence:
                sentence = sentence + " " + elem[1]
            else:
                sentence = elem[1]
        return sentence

    # This method performs a GET request to the cloud to get the initial sentence and the dialogue state that will be used
    # for all the speakers. Then, it initializes the speakers stats and speakers info data.
    def acquire_initial_state(self):
        # Registration of the first "unknown" user
        # Try to contact the server
        resp = requests.get("http://" + self.server_ip + ":5000/CAIR_hub", verify=False)
        first_dialogue_sentence = resp.json()["first_sentence"]
        dialogue_state = resp.json()['dialogue_state']

        # If the server is not up, continue trying until a response is received
        if not dialogue_state:
            self.animated_speech.say(self.voice_speed + "I'm waiting for the server...", self.configuration)
            # Keep on trying to perform requests to the server until it is reachable.
            while not dialogue_state:
                resp = requests.get("http://" + self.server_ip + ":5000/CAIR_hub", verify=False)
                dialogue_state = resp.json()['dialogue_state']
                time.sleep(1)
        # Store the dialogue state in the corresponding file
        with open(self.dialogue_state_file_path, 'w') as f:
            json.dump(dialogue_state, f, ensure_ascii=False, indent=4)

        profile_id = "00000000-0000-0000-0000-000000000000"
        # Add the info of the new profile to the file where the key is the profile id and the values are the info (name)
        with open(self.speakers_info_file_path, 'w') as f:
            json.dump({profile_id: {"name": "User", "gender": 'nb'}},
                      f, ensure_ascii=False, indent=4)

        # Initialize dialogue statistics
        dialogue_statistics = DialogueStatistics(profile_id=profile_id)
        # Update the stats in the file
        with open(self.dialogue_statistics_file_path, 'w') as f:
            json.dump(dialogue_statistics.to_dict(), f, ensure_ascii=False, indent=4)

        return first_dialogue_sentence

    # This method updates the info and the statistics of the users when a new user registers
    def add_speaker_statistics(self, new_speaker_info):
        # Load the information about the already existing users to add the new user
        with open(self.speakers_info_file_path, 'r') as info:
            speakers_info = json.load(info)
        # Load the statistics about the interactions with existing users to update them
        with open(self.dialogue_statistics_file_path, 'r') as stats:
            dialogue_statistics = DialogueStatistics(d=json.load(stats))
        # Increase the size of the matrices and of the lists and add the new profile id to the list of mapped speakers
        dialogue_statistics.add_new_speaker_statistics(new_speaker_info.profile_id)
        # Update the stats in the file
        with open(self.dialogue_statistics_file_path, 'w') as f:
            json.dump(dialogue_statistics.to_dict(), f, ensure_ascii=False, indent=4)

        # Add the info of the new profile to the file where the key is the profile id and the values are the info (name)
        user_gender = new_speaker_info.gender.translate(str.maketrans('', '', string.punctuation)).lower()
        female_list = ["female", "femmina", "femminile", "donna"]
        male_list = ["male", "maschio", "maschile", "uomo"]
        if any(word in user_gender for word in female_list):
            user_gender = "f"
        elif any(word in user_gender for word in male_list):
            user_gender = "m"
        else:
            user_gender = "nb"

        speakers_info[new_speaker_info.profile_id] = {"name": new_speaker_info.name, "gender": user_gender}
        with open(self.speakers_info_file_path, 'w') as f:
            json.dump(speakers_info, f, ensure_ascii=False, indent=4)

        return speakers_info, dialogue_statistics

    # This function performs the registration of a new speaker on the Microsoft APIs
    def registration_procedure(self):
        # Establish a socket connection with the registration.py script
        client_registration_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_registration_socket.connect((self.registration_ip, 9091))
        # ** STEP 1 ** Create a new profile ID
        self.logger("Creating new profile ID")
        client_registration_socket.send(b"new_profile_id")
        new_profile_id = client_registration_socket.recv(256).decode('utf-8')

        # ** STEP 2 ** Ask the name to the user
        if self.language == "it":
            to_say = "Per favore, dimmi come ti chiami."
        else:
            to_say = "Please, tell me your name."
        self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        client_registration_socket.send(b"new_profile_name")
        new_profile_name = client_registration_socket.recv(256).decode('utf-8')

        # ** STEP 3 ** Ask the gender to the user
        if self.language == "it":
            to_say = "Per favore, dimmi quale pronome di genere vuoi che usi quando parlo con te: femminile, maschile o neutro?"
        else:
            to_say = "Please, tell me which gender pronoun should I use when I talk with you: male, female or neutral?"
        self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        client_registration_socket.send(b"new_profile_gender")
        new_profile_gender = client_registration_socket.recv(256).decode('utf-8')

        # ** STEP 4 ** Ask the user to talk for 20 seconds
        if self.language == "it":
            to_say = "Per favore, parla per 20 secondi in modo che io possa imparare a riconoscere la tua voce."
        else:
            to_say = "Please, talk for 20 seconds so that I can learn to recognize your voice."
        self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        client_registration_socket.send(b"new_profile_enrollment")
        # Wait for the completion of the enrollment
        self.logger("*** Listening ***")
        client_registration_socket.recv(1024).decode('utf-8')
        if self.language == "it":
            to_say = "Grazie per aver completato la registrazione " + new_profile_name + "! D'ora in poi riconoscerò la tua voce!"
        else:
            to_say = "Thank you for registering " + new_profile_name + "! From now on I will recognize your voice."
        self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        new_speaker_info = SpeakerInfo(new_profile_id, new_profile_name, new_profile_gender)
        # This function updates the info and the statistics of the users, adding the new profile id and the name to the
        # speakers_info and increasing the dimensions of the structures contained in the dialogue statistics.
        speakers_info, dialogue_statistics = self.add_speaker_statistics(new_speaker_info)
        return speakers_info, dialogue_statistics
