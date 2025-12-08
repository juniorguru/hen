# MenuGenerator
***Program which randomly chooses meals for a whole week***

-> without valid email and your password key it will not work! <-

-- Requirments -- <br />
-> module Tkinter <br />
-> module pathlib <br />
-> module os <br />
-> module random <br />
-> module smtplib <br />
-> module email.message (EmailMesssage) <br />
-> all the files <br />
-> your own email adress and password to give access to program to send emails <br />

Almost three times a week we discuss what to cook for lunches. Pretty hard to figure it out sometimes :D 
So I decided to write a program which will help. 
And here it is! 

This program use .txt file with names of meals and randomly picks one, four or seven of them. 

![menu_generator](https://user-images.githubusercontent.com/110200002/228265914-4da84468-6479-4ae8-8a82-157b1751f5b4.jpg)

After making a list of chosen meals the program will use one of two basic menu templates (one if you want each day different meal - compatibile with 7 random meals, or another one which is comatibile with 4 random meals (so three meals are for two days)) and it will fill the chosen meals into the template. 
Also the program can send the complete menu to the email, so it can be printed out.  

Finally there is also posibility to add new meals to the .txt file. 

The UI of the program is in Czech language, so I can show it also to my husband or mother-in-law :-)
But the code is in English, so feel free to check it out! 


![2023-03-28 (6)](https://user-images.githubusercontent.com/110200002/228290673-6d1cad45-0eac-4888-ac46-681d4637b7d9.png)

Messagebox with information, that new meal was succesfully added.

![2023-03-28 (3)](https://user-images.githubusercontent.com/110200002/228266096-01fb34af-bb49-48c0-9854-2c7409119d3e.png)

Messagebox that tells user that the meal the user wants to add is already in the file.

![2023-03-28 (4)](https://user-images.githubusercontent.com/110200002/228266107-6b022756-f009-4d23-9e0d-830ab6fe9414.png)

And also messagebox with confirmation that the menu was succesfully sent.

![2023-03-28 (2)](https://user-images.githubusercontent.com/110200002/228266118-90218f2d-f340-4232-8ad1-57d1dd89b5c4.png)
