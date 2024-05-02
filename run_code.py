import champ_placement as chp

#initialise the class
show = chp.champ_placement()


# # # REMOVE (and replace other) HASHTAG TO CHOOSE BETWEEN INPUT OR LGE # # #
# height = input("Enter Height 'Sml', 'Med'', 'Int' or 'Lge': ")
height = "Lge"


heights = ['Sml', 'Med', 'Int', 'Lge']
assert height in heights

#get the top 20 by calling index 0
#get the overall results by index = 1
index = 1

# print(show.recent_show_link())
print(show.overall_results(height)[index])
