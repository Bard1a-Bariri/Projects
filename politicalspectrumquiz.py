import matplotlib.pyplot as plt

print("-----Political Spectrum Test-----")
quiz = [
    {
        "question": "High-income earners and large corporations should be taxed at a significantly higher rate to fund public services and reduce wealth inequality.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "x",
        "weights": {
            "A": -2,      
            "B": -1,   
            "C": 1,         
            "D": 2            
        }
    },
    {
        "question": "Essential services like healthcare and education should be publicly funded and run by the government, rather than operated as private businesses.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "x",
        "weights": {
            "A": -2,   
            "B": -1,        
            "C": 1,           
            "D": 2            
        }
    },
    {
        "question": "The government should strictly regulate private businesses to protect consumers, workers, and the environment.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "x",
        "weights": {
            "A": -2,   
            "B": -1,   
            "C": 1,    
            "D": 2     
        }
    },
    {
        "question": "Societies function best when they preserve traditional cultural values and family structures rather than constantly seeking social progress.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "y",
        "weights": {
            "A": 2,    
            "B": 1,    
            "C": -1,   
            "D": -2    
        }
    },
    {
        "question": "A nation must maintain strict controls over its borders and immigration to protect its national identity, security, and economy.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "y",
        "weights": {
            "A": 2,    
            "B": 1,    
            "C": -1,   
            "D": -2    
        }
    },
    {
        "question": "The government should actively promote diversity and implement policies to correct historical disadvantages faced by minority groups.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "y",
        "weights": {
            "A": -2,   
            "B": -1,   
            "C": 1,    
            "D": 2     
        }
    },
    {
        "question": "It is acceptable for the government to monitor citizens' communications and restrict certain liberties if it guarantees national security and prevents crime.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "y",
        "weights": {
            "A": 2,    
            "B": 1,    
            "C": -1,   
            "D": -2    
        }
    },
    {
        "question": "Freedom of speech should be absolute, even if it includes statements that are highly offensive, controversial, or politically extreme.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "y",
        "weights": {
            "A": -2,   
            "B": -1,   
            "C": 1,   
            "D": 2     
        }
    },
    {
        "question": "Adults should have the absolute freedom to make choices regarding their own bodies and lifestyles (such as drug use or medical choices) as long as they do not harm others.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "y",
        "weights": {
            "A": -2,   
            "B": -1,   
            "C": 1,    
            "D": 2     
        }
    },
    {
        "question": "Without a strong government and strict laws to maintain order, society would quickly deteriorate into chaos.",
        "choices": {
            "A": "Strongly Agree",
            "B": "Agree",
            "C": "Disagree",
            "D": "Strongly Disagree"
        },
        "axis": "y",
        "weights": {
            "A": 2,    
            "B": 1,   
            "C": -1,   
            "D": -2    
        }
    }
]


user_x = 0
user_y = 0
for index, item in enumerate(quiz, 1):
    print(f"Question {index}: {item['question']}")
    for letter, choice in item["choices"].items():
      print(f"  {letter}: {choice}")
  
    answer = input("Your answer (A/B/C/D): ").strip().upper()
    change = item["weights"][answer]
    if item["axis"] == "y":
      user_y += change
    elif item["axis"] == "x":
      user_x += change
    
    
fig, ax = plt.subplots(figsize=(8, 8))
ax.axhline(0, color='black', linewidth=2)  
ax.axvline(0, color='black', linewidth=2) 
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)

ax.set_xticks([])
ax.set_yticks([])

ax.axvspan(-10, 0, ymin=0.5, ymax=1.0, facecolor='#FF9999', alpha=0.5, zorder=1)
ax.axvspan(0, 10, ymin=0.5, ymax=1.0, facecolor='#99CCFF', alpha=0.5, zorder=1)
ax.axvspan(-10, 0, ymin=0.0, ymax=0.5, facecolor='#99FF99', alpha=0.5, zorder=1)
ax.axvspan(0, 10, ymin=0.0, ymax=0.5, facecolor='#D1BBFF', alpha=0.5, zorder=1)

ax.text(0, 9.3, "AUTHORITARIAN", fontsize=12, fontweight='bold', ha='center', va='center')
ax.text(0, -9.3, "LIBERTARIAN", fontsize=12, fontweight='bold', ha='center', va='center')
ax.text(-9.5, 0.5, "ECONOMIC LEFT", fontsize=12, fontweight='bold', ha='left', va='center')
ax.text(9.5, 0.5, "ECONOMIC RIGHT", fontsize=12, fontweight='bold', ha='right', va='center')

ax.scatter(user_x, user_y, color='red', edgecolor='black', s=250, marker='X', zorder=3)
ax.text(user_x, user_y - 0.8, "YOU", fontsize=10, fontweight='bold', ha='center', zorder=3)

plt.title("Your position on the political spectrum:", pad=15, fontsize=14)

plt.savefig("political_spectrum_result.png", dpi=300, bbox_inches='tight')