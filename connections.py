import json
import sys
import random
import os

def friendly_assert(condition, message):
    if not condition:
        print(message)
        sys.exit(1)

def read_word_groups(filename):
    with open(filename, 'r') as file:
        word_groups = [line.strip().upper().split() for line in file]
    
    # Assert that all groups have the same size
    group_size = len(word_groups[0])
    friendly_assert(all(len(group) == group_size for group in word_groups), "All groups must be of the same size.")

    return word_groups


def shuffle_words(word_groups):
    # Combine all words into a single list and convert to uppercase
    all_words = [word for group in word_groups for word in group]
    # Shuffle the combined list of words
    random.shuffle(all_words)
    return all_words

def create_puzzle_html(shuffled_words, original_word_groups):
    words_json = json.dumps(shuffled_words)
    original_groups_json = json.dumps(original_word_groups)
    group_size = len(original_word_groups[0])

    # Define a list of colors for the completed groups
    colors = ["#F3DE7D", "#B2C4EB", "#A7C168", "#B085C2", "#90DFC0", "#E88A8B", "#E4C382", "#E9AFD9"]
    friendly_assert(len(original_word_groups) <= len(colors), f"Maximum of {len(colors)} groups allowed.")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connections Puzzle</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .word-group {{
            display: flex;
            justify-content: start;
            margin-bottom: 20px;
        }}
        .word {{
            cursor: pointer;
            padding: 5px;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            width: 100px; /* Fixed width */
            height: 30px; /* Fixed height */
            margin: 5px;
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            box-sizing: border-box;
            text-align: center;
        }}
        .selected {{ background-color: #add8e6; }}
        .completed-group {{ margin-bottom: 10px; }}
        .incorrect-group span {{ background-color: #f0f0f0; }} /* Gray background for incorrect guesses */
    </style>
    </head>
    <body>
        <div id="puzzle" class="puzzle">
            <!-- The puzzle will be generated here -->
        </div>
        <div id="completedGroups" class="completed-groups">
            <h3>Completed Groups</h3>
            <!-- Completed groups will be shown here -->
        </div>
        <div id="incorrectGuessesContainer">
            <h3>Incorrect Guesses</h3>
            <div id="incorrectGuesses" class="incorrect-guesses">
                <!-- Incorrect guesses will be shown here -->
            </div>
        </div>
        <button id="checkButton" disabled>Check</button>
        <script>
        document.addEventListener('DOMContentLoaded', (event) => {{
            let shuffledWords = {words_json};
            const originalWordGroups = {original_groups_json};
            const colors = {json.dumps(colors)};
            const puzzleDiv = document.getElementById('puzzle');
            const completedDiv = document.getElementById('completedGroups');
            const incorrectDiv = document.getElementById('incorrectGuesses');
            const checkButton = document.getElementById('checkButton');

            let completedGroups = [];

            // Function to create word groups
            function createWordGroups() {{
                puzzleDiv.innerHTML = ''; // Clear existing words
                for (let i = 0; i < shuffledWords.length; i += {group_size}) {{
                    const groupDiv = document.createElement('div');
                    groupDiv.className = 'word-group';
                    for (let j = i; j < i + {group_size} && j < shuffledWords.length; j++) {{
                        const word = shuffledWords[j];
                        const wordSpan = document.createElement('span');
                        wordSpan.className = 'word';
                        wordSpan.textContent = word;
                        wordSpan.dataset.word = word; // Keep track of the word itself
                        wordSpan.addEventListener('click', () => {{
                            if (!completedGroups.flat().includes(word)) {{
                                wordSpan.classList.toggle('selected');
                                updateCheckButtonState();
                            }}
                        }});
                        groupDiv.appendChild(wordSpan);
                    }}
                    puzzleDiv.appendChild(groupDiv);
                }}
                adjustWordFontSize();
            }}

            function adjustWordFontSize() {{
                document.querySelectorAll('.word').forEach(wordSpan => {{
                    let fontSize = 16; // Start with initial font size
                    while (wordSpan.scrollWidth > wordSpan.offsetWidth) {{
                        fontSize--;
                        wordSpan.style.fontSize = fontSize + 'px';
                    }}
                }});
            }}

            // Function to update the state of the check button
            function updateCheckButtonState() {{
                const selectedCount = document.querySelectorAll('.word.selected').length;
                checkButton.disabled = selectedCount !== {group_size};
            }}

            createWordGroups(); // Initially create word groups

            checkButton.addEventListener('click', () => {{
                const selectedWords = Array.from(document.querySelectorAll('.word.selected')).map(w => w.textContent);
                let isCorrect = false;

                for (const group of originalWordGroups) {{
                    if (group.length === selectedWords.length && group.every(word => selectedWords.includes(word))) {{
                        isCorrect = true;
                        const groupIndex = originalWordGroups.indexOf(group);
                        const completedGroupDiv = document.createElement('div');
                        completedGroupDiv.className = 'completed-group';

                        group.forEach(word => {{
                            const completedWordSpan = document.createElement('span');
                            completedWordSpan.className = 'word';
                            completedWordSpan.textContent = word;
                            completedWordSpan.style.backgroundColor = colors[groupIndex];
                            completedGroupDiv.appendChild(completedWordSpan);
                        }});

                        completedDiv.appendChild(completedGroupDiv);
                        completedGroups.push(group);

                        // Remove guessed words from shuffledWords
                        shuffledWords = shuffledWords.filter(w => !group.includes(w));
                        createWordGroups(); // Recreate word groups to fill gaps
                        updateCheckButtonState();
                        break;
                    }}
                }}

                if (!isCorrect) {{
                    const incorrectGroupDiv = document.createElement('div');
                    incorrectGroupDiv.className = 'incorrect-group';

                    selectedWords.forEach(word => {{
                        const wordSpan = document.createElement('span');
                        wordSpan.className = 'word';
                        wordSpan.textContent = word;
                        incorrectGroupDiv.appendChild(wordSpan);
                    }});

                    incorrectDiv.appendChild(incorrectGroupDiv);
                    document.querySelectorAll('.word.selected').forEach(wordSpan => {{
                        wordSpan.classList.remove('selected');
                    }});
                    updateCheckButtonState();
                }}
            }});
        }});
        </script>
    </body>
    </html>
    """
    return html_content

def save_puzzle(shuffled_words, original_word_groups, filename):
    html_content = create_puzzle_html(shuffled_words, original_word_groups)
    with open(filename, 'w') as file:
        file.write(html_content)
    print(f"Puzzle saved to {filename}")

def get_output_filename(input_filename):
    directory = os.path.dirname(input_filename)
    base_name = os.path.basename(input_filename)
    output_base_name = base_name.replace('.txt', '.html')
    return os.path.join(directory, output_base_name)

def main():
    # Check if a filename is provided as a command-line argument
    friendly_assert(len(sys.argv) >= 2, "Usage: python3 connections.py <input file>")
    input_filename = sys.argv[1]
    friendly_assert(input_filename.endswith(".txt"), "Input must be a .txt file.")
    original_word_groups = read_word_groups(input_filename)
    shuffled_words = shuffle_words(original_word_groups)
    output_filename = get_output_filename(input_filename)

    # Pass shuffled_words for display and original_word_groups for checking
    save_puzzle(shuffled_words, original_word_groups, output_filename)

if __name__ == "__main__":
    main()