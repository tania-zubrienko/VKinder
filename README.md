# VKinder
A chatbot created for the social network VK.com. The script is consuming the official API designed by VK.com

The logic is the following: 
1) When the script runs, the connection to PostgresDB is created. 
2) The authorised user starts the conversation with the bot by typing /start
3) The bot asks a couple of questions to the user about their preferences (age, location, relationship status) 
and after that searches open accounts of those users who matches the criterea showing 3 photos
4) The authorised user can Like or Dislike the profile
5) If the profile is "Liked" the bot returns the link to a liked-user´s account to be able to send a message, and the id of this profile is saved into a database "white-list"
6) If the profile is "disliked" the id is saved into "black-list" of a database 
7) The execution of the script guarantess that the profiles won´t be repeated. 
8) Only profiles which are open for public are shown
