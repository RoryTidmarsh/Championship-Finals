import champ_placement as chp
import sys
import warnings
warnings.filterwarnings("ignore")

#initialise the class
show = chp.champ_placement()

if len(sys.argv) > 1:
    height = sys.argv[1].capitalize()
else:
    height = input("Enter Height 'Sml', 'Med'', 'Int' or 'Lge': ")

height = height.capitalize()

#
heights = ['Sml', 'Med', 'Int', 'Lge']
assert height in heights

#get the top 20 by calling index 0
#get the overall results by index = 1
index = 1

# print(show.recent_show_link())
print(show.overall_results(height)[index])
