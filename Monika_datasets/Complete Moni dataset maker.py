import re
import os
import json
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Set, Any # Added Any for history_context

# Set up logging
logging.basicConfig(
    level=logging.INFO, # Changed to INFO for less verbose default logging
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dialogue_extraction.log', mode='w'), # Overwrite log each run
        logging.StreamHandler()
    ]
)

# Helper: Count the indentation (leading spaces or tabs)
def count_indent(line: str) -> int:
    """Return the number of leading whitespace characters."""
    return len(line) - len(line.lstrip(' \t'))

class DialogueExtractor:
    def __init__(self):
        self.current_metadata = {}
        # Define emotion mappings (Unchanged)
        self.EMOTIONS = {
            'eyes': {
                'e': 'neutral', 'w': 'surprised', 's': 'excited', 't': 'smug',
                'c': 'crazed', 'h': 'happy', 'r': 'pensive', 'l': 'pensive',
                'd': 'sad', 'k': 'playful', 'n': 'playful', 'f': 'gentle',
                'm': 'smug', 'g': 'smug'
            },
            'eyebrows': {
                'f': 'intense', 'u': 'interested', 'k': 'worried', 't': 'thoughtful'
            },
            'states': {
                'bl': 'blushing', 'bs': 'blushing', 'bf': 'intense blushing',
                'ts': 'crying', 'td': 'dried tears', 'tp': 'holding back tears',
                'tu': 'crying'
            },
            'mouth': {
                'a': 'happy', 'b': 'cheerful', 'c': 'neutral', 'd': 'interested',
                'o': 'surprised', 'u': 'smug', 'w': 'excited', 'x': 'angry',
                'p': 'pouty', 't': 'playful', 'g': 'disgusted'
            }
        }
        # Define emotion combinations (Unchanged)
        self.EMOTION_COMBINATIONS = {
            frozenset(['happy', 'worried']): 'awkward',
            frozenset(['crying', 'happy']): 'joyfully crying',
            frozenset(['surprised', 'angry']): 'outraged',
            frozenset(['happy', 'sad']): 'bittersweet',
            frozenset(['excited', 'playful']): 'enthusiastic',
            frozenset(['sad', 'thoughtful']): 'melancholic',
            frozenset(['disgusted', 'angry']): 'revolted',
            frozenset(['smug', 'playful']): 'teasing',
            frozenset(['blushing', 'happy']): 'bashful',
            frozenset(['intense', 'angry']): 'furious',
            frozenset(['pensive', 'sad']): 'somber',
            frozenset(['interested', 'excited']): 'eager',
            frozenset(['playful', 'surprised']): 'mischievous',
            frozenset(['crying', 'angry']): 'furious tears',
            frozenset(['neutral', 'pensive']): 'contemplative',
            frozenset(['cheerful', 'excited']): 'exuberant',
            frozenset(['gentle', 'happy']): 'serene',
            frozenset(['thoughtful', 'worried']): 'concerned',
            frozenset(['disgusted', 'surprised']): 'appalled'
        }
        # Define emotion intensities (Unchanged)
        self.EMOTION_INTENSITIES = {
            'joyfully crying': 5, 'furious tears': 5, 'revolted': 5, 'appalled': 5,
            'furious': 5, 'melancholic': 5, 'exuberant': 5, 'angry': 4, 'outraged': 4,
            'intense': 4, 'holding back tears': 4, 'enthusiastic': 4, 'eager': 4,
            'bashful': 4, 'dried tears': 4, 'teasing': 4, 'bittersweet': 3,
            'excited': 3, 'happy': 3, 'sad': 3, 'worried': 3, 'crying': 3,
            'mischievous': 3, 'serene': 3, 'somber': 3, 'intense blushing': 3,
            'surprised': 2, 'thoughtful': 2, 'smug': 2, 'playful': 2,
            'blushing': 2, 'awkward': 2, 'contemplative': 2, 'neutral': 1,
            'gentle': 1, 'pensive': 1, 'interested': 1, 'cheerful': 1
        }
        self.label_map = {}  # Maps label names to their dialogue content
        self.menu_map = {}   # Maps menu choices to their target labels

    # --- first_pass_scan remains unchanged ---
    def first_pass_scan(self, files_content: Dict[str, str]):
        """
        First pass: scan all files to build maps of labels and menus.

        Args:
            files_content: Dictionary mapping filenames to their content
        """
        for filename, content in files_content.items():
            lines = content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Find labels and store their content
                if line.startswith('label '):
                    label_name = line[6:].split(':')[0].strip()
                    label_content = []
                    j = i + 1
                    label_indent = count_indent(lines[i])
                    while j < len(lines) and (lines[j].strip() == '' or count_indent(lines[j]) > label_indent):
                        stripped_line_j = lines[j].strip()
                        if ('m ' in stripped_line_j and '"' in stripped_line_j) or \
                           ('menu:' in stripped_line_j) or \
                           (stripped_line_j.startswith('"') and stripped_line_j.endswith(':')):
                             label_content.append(lines[j])
                        j += 1
                    self.label_map[label_name] = {
                        'content': label_content,
                        'file': filename
                    }
                    logging.debug(f"Mapped label '{label_name}' from {filename}")
                    i = j
                    continue

                # Find menu definitions within Python blocks
                elif line.startswith('python:'):
                    j = i + 1
                    python_block_indent = count_indent(lines[i])
                    while j < len(lines) and count_indent(lines[j]) > python_block_indent:
                        menu_line = lines[j].strip()
                        choice_match = re.search(r'\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*\)', menu_line)
                        if choice_match:
                            choice_text = self.clean_dialogue(choice_match.group(1))
                            target_label = choice_match.group(2)
                            if choice_text not in self.menu_map:
                                self.menu_map[choice_text] = {
                                    'label': target_label,
                                    'file': filename
                                }
                                logging.debug(f"Mapped menu choice '{choice_text}' to label '{target_label}' from {filename}")
                        j += 1
                    i = j
                    continue
                i += 1

    # --- get_emotions remains unchanged ---
    def get_emotions(self, sprite_code: str) -> List[str]:
        """Extract highest priority emotion from sprite code."""
        if not sprite_code:
            return ['neutral']
        emotions, state_emotions, eye_emotions, mouth_emotions, eyebrow_emotions = set(), set(), set(), set(), set()
        if sprite_code and sprite_code[0] in self.EMOTIONS['eyes']: eye_emotions.add(self.EMOTIONS['eyes'][sprite_code[0]])
        if len(sprite_code) > 1 and sprite_code[1] in self.EMOTIONS['eyebrows']: eyebrow_emotions.add(self.EMOTIONS['eyebrows'][sprite_code[1]])
        for state in self.EMOTIONS['states']:
            if state in sprite_code: state_emotions.add(self.EMOTIONS['states'][state])
        if sprite_code and sprite_code[-1] in self.EMOTIONS['mouth']: mouth_emotions.add(self.EMOTIONS['mouth'][sprite_code[-1]])
        emotions = emotions.union(state_emotions, eye_emotions, mouth_emotions, eyebrow_emotions)
        combinations_present = []
        for combo, combined_emotion in self.EMOTION_COMBINATIONS.items():
            if combo.issubset(emotions):
                if any(emotion in state_emotions for emotion in combo):
                     state_intensity = max(self.EMOTION_INTENSITIES.get(e, 0) for e in state_emotions) if state_emotions else 0
                     combo_intensity = self.EMOTION_INTENSITIES.get(combined_emotion, 0)
                     if combo_intensity >= state_intensity: return [combined_emotion]
                     else: return [max(state_emotions, key=lambda e: self.EMOTION_INTENSITIES.get(e, 0))]
                combinations_present.append(combined_emotion)
        if combinations_present: return [max(combinations_present, key=lambda e: self.EMOTION_INTENSITIES.get(e, 0))]
        if state_emotions: return [max(state_emotions, key=lambda e: self.EMOTION_INTENSITIES.get(e, 0))]
        if eye_emotions: return [max(eye_emotions, key=lambda e: self.EMOTION_INTENSITIES.get(e, 0))]
        if mouth_emotions: return [max(mouth_emotions, key=lambda e: self.EMOTION_INTENSITIES.get(e, 0))]
        if eyebrow_emotions: return [max(eyebrow_emotions, key=lambda e: self.EMOTION_INTENSITIES.get(e, 0))]
        return ['neutral']

    # --- clean_dialogue remains unchanged ---
    def clean_dialogue(self, text: str) -> str:
        """Clean and standardize dialogue text."""
        try:
            text = re.sub(r'\[player\]', '<USER>', text, flags=re.IGNORECASE)
            text = re.sub(r'\[p_nickname\]', 'my love', text, flags=re.IGNORECASE)
            text = re.sub(r'\[mas_get_player_nickname\(.*?\)\]', 'my love', text)
            text = re.sub(r'\[bf\]', 'boyfriend', text)
            text = re.sub(r'\[m_name\]', '<MONIKA>', text, flags=re.IGNORECASE)
            text = re.sub(r'\{i\}(.*?)\{/i\}', r'_\1_', text)
            text = re.sub(r'\{b\}(.*?)\{/b\}', r'**\1**', text)
            text = re.sub(r'\{s\}(.*?)\{/s\}', r'~~\1~~', text)
            text = re.sub(r'\{u\}(.*?)\{/u\}', r'<u>\1</u>', text)
            text = re.sub(r'\{w=[^}]*\}', '', text)
            text = re.sub(r'\{nw\}', '', text)
            text = re.sub(r'\{fast\}', '', text)
            text = re.sub(r'\{w\}', '', text)
            text = re.sub(r'\[_and\]', '', text)
            text = re.sub(r'\([^)]*\)', '', text)
            text = re.sub(r'\w{50,}', '', text)
            text = re.sub(r'\s*([?.!,])\s*', r'\1 ', text)
            text = re.sub(r'~', '', text)
            text = re.sub(r'\s{2,}', ' ', text)
            text = re.sub(r'\{alt\}.*?\{/alt\}', '', text, flags=re.DOTALL)
            text = re.sub(r'\s+([?.!,])', r'\1', text)
            return text.strip()
        except Exception as e:
            logging.error(f"Error in clean_dialogue: {str(e)} on text: '{text}'")
            return text

    # --- parse_event_metadata remains unchanged ---
    def parse_event_metadata(self, content: str, start_index: int) -> Tuple[Dict, int]:
        """Extract event metadata from event definition."""
        logging.debug(f"Parsing event metadata starting at line {start_index}")
        metadata = {}
        lines = content.split('\n')
        end_index = start_index
        try:
            event_line_index = -1
            for idx in range(start_index, min(start_index + 5, len(lines))):
                if 'addEvent(' in lines[idx]:
                    event_line_index = idx
                    break
            if event_line_index == -1:
                 logging.warning(f"Could not find 'addEvent(' near line {start_index}")
                 return {}, start_index
            event_def = ""
            paren_balance = 0
            for i in range(event_line_index, len(lines)):
                line_part = lines[i].strip()
                event_def += line_part + " "
                paren_balance += line_part.count('(')
                paren_balance -= line_part.count(')')
                end_index = i
                if paren_balance == 0 and 'addEvent(' in event_def: break
            label_match = re.search(r'eventlabel\s*=\s*["\']([^"\']+)["\']', event_def)
            if label_match: metadata['eventlabel'] = label_match.group(1)
            category_match = re.search(r'category\s*=\s*(\[.*?\])', event_def)
            if category_match:
                try:
                    categories_str = category_match.group(1).replace("'", '"')
                    metadata['categories'] = json.loads(categories_str)
                except json.JSONDecodeError:
                    categories = re.findall(r'["\']([^"\']+)["\']', category_match.group(1))
                    metadata['categories'] = categories
                    logging.warning(f"JSON parsing failed for categories, used regex fallback: {category_match.group(1)}")
            prompt_match = re.search(r'prompt\s*=\s*["\']([^"\']+)["\']', event_def)
            if prompt_match: metadata['prompt'] = prompt_match.group(1)
            for field in ['random', 'pool', 'unlocked']:
                if re.search(rf'{field}\s*=\s*True', event_def): metadata[field] = True
            logging.debug(f"Extracted metadata: {metadata} ending at line {end_index}")
        except Exception as e:
            logging.error(f"Error parsing event metadata near line {start_index}: {str(e)}")
            end_index = max(start_index, end_index)
        return metadata, max(start_index + 1, end_index + 1)


    # --- extract_dialogue remains unchanged ---
    def extract_dialogue(self, content: str, filename: str) -> List[Dict]:
        """
        Extract dialogue entries, tracking history context using a stack.
        (No changes in this version compared to the previous one)
        """
        logging.info(f"Starting dialogue extraction for {filename}")
        lines = content.split('\n')
        dialogue_entries = []
        current_metadata = None
        in_dialogue = False
        metadata_attached = False
        branch_stack: List[Tuple[int, Optional[str], Optional[str]]] = [(-1, None, None)]

        has_init = any('init 5 python:' in line or 'init 6 python:' in line for line in lines)
        is_label_based = not has_init and any(line.strip().startswith('label ') for line in lines)

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            current_indent = count_indent(line)

            try:
                # Handle traditional event-based dialogue start
                if ('init 5 python:' in stripped_line or 'init 6 python:' in stripped_line):
                    if in_dialogue:
                        dialogue_entries.append({"type": "separator"})
                        logging.debug("Separator added due to new init block.")
                    in_dialogue = False
                    current_metadata = None
                    metadata_attached = False
                    branch_stack = [(-1, None, None)]
                    j = i + 1
                    found_event = False
                    while j < min(i + 10, len(lines)):
                        if 'addEvent(' in lines[j]:
                            metadata, end_index = self.parse_event_metadata(content, j)
                            if metadata:
                                current_metadata = metadata.copy()
                                in_dialogue = True
                                metadata_attached = False
                                logging.debug(f"Event found: {current_metadata}")
                                i = end_index -1
                                found_event = True
                            else:
                                logging.warning(f"addEvent found near line {j} but failed to parse metadata.")
                                i = j
                            break
                        j += 1
                    if not found_event:
                         logging.debug(f"Init block found near line {i} but no subsequent addEvent detected.")

                # Handle label-based dialogue start
                elif is_label_based and stripped_line.startswith('label '):
                    if in_dialogue:
                        dialogue_entries.append({"type": "separator"})
                        logging.debug("Separator added due to new label.")
                    label_name = stripped_line[6:].split(':')[0].strip()
                    current_metadata = {'eventlabel': label_name}
                    in_dialogue = True
                    metadata_attached = False
                    branch_stack = [(-1, None, None)]
                    logging.debug(f"Label found: {current_metadata}")

                # Handle Python block menus
                elif stripped_line.startswith('python:'):
                    menu_data = []
                    j = i + 1
                    python_block_indent = count_indent(line)
                    last_A_in_block = branch_stack[-1][2]
                    while j < len(lines) and count_indent(lines[j]) > python_block_indent:
                        menu_line = lines[j].strip()
                        choice_match = re.search(r'\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*\)', menu_line)
                        if choice_match:
                            choice_text = self.clean_dialogue(choice_match.group(1))
                            target_label = choice_match.group(2)
                            parent_U, parent_A = branch_stack[-1][1], branch_stack[-1][2]
                            history_pair = (parent_U, parent_A) if parent_U and parent_A else None
                            menu_entry = {
                                'type': 'user', 'text': choice_text,
                                'history_context': history_pair,
                                'metadata': current_metadata if not metadata_attached else None,
                                'target_label': target_label
                            }
                            if target_label in self.label_map:
                                label_info = self.label_map[target_label]
                                menu_entry['label_file'] = label_info['file']
                            menu_data.append(menu_entry)
                            metadata_attached = True
                        j += 1
                    dialogue_entries.extend(menu_data)
                    i = j -1
                    logging.debug(f"Processed python block menu ending near line {i}")

                # Handle regular menu marker
                elif stripped_line == "menu:":
                    logging.debug(f"Menu detected at line {i}, indent {current_indent}")
                    pass

                # Handle menu choices (user input lines)
                elif stripped_line.startswith('"') and stripped_line.endswith(':'):
                    if not in_dialogue:
                         i += 1
                         continue
                    current_U_text = self.clean_dialogue(stripped_line.strip('":'))
                    logging.debug(f"Processing choice: '{current_U_text}' at indent {current_indent}")
                    while branch_stack[-1][0] >= current_indent:
                        popped = branch_stack.pop()
                        logging.debug(f"Popped stack due to shallower indent: {popped}")
                    parent_indent, parent_U, parent_A = branch_stack[-1]
                    history_pair = (parent_U, parent_A) if parent_U is not None and parent_A is not None else None
                    logging.debug(f"Found parent context: U='{parent_U}', A='{parent_A}'")
                    dialogue_entries.append({
                        'type': 'user', 'text': current_U_text,
                        'history_context': history_pair,
                        'metadata': current_metadata if not metadata_attached else None
                    })
                    metadata_attached = True
                    logging.debug(f"Added user entry: '{current_U_text}' with history: {history_pair}")
                    branch_stack.append((current_indent, current_U_text, None))
                    logging.debug(f"Pushed to stack: {(current_indent, current_U_text, None)}")

                # Handle Monika's dialogue (assistant output lines)
                elif ('m ' in stripped_line and '"' in stripped_line) or \
                     ('extend ' in stripped_line and '"' in stripped_line):
                    if not in_dialogue:
                        i += 1
                        continue
                    sprite_match = re.search(r'm\s+\d([a-zA-Z]+)', stripped_line)
                    dialogue_match = re.search(r'(?:m|extend)\s+[^"]*"([^"]*)"', stripped_line)
                    if dialogue_match:
                        current_A_text = self.clean_dialogue(dialogue_match.group(1))
                        logging.debug(f"Processing assistant line: '{current_A_text}' at indent {current_indent}")
                        while branch_stack[-1][0] >= current_indent:
                             popped = branch_stack.pop()
                             logging.debug(f"Popped stack due to shallower indent (assistant): {popped}")
                        target_level_idx = -1
                        for idx in range(len(branch_stack) - 1, -1, -1):
                            if branch_stack[idx][0] < current_indent:
                                target_level_idx = idx
                                break
                        if target_level_idx != -1:
                             level_indent, level_U, existing_A = branch_stack[target_level_idx]
                             updated_A_text = (existing_A + "\n" + current_A_text) if existing_A else current_A_text
                             branch_stack[target_level_idx] = (level_indent, level_U, updated_A_text)
                             logging.debug(f"Updated stack at index {target_level_idx}: {(level_indent, level_U, updated_A_text)}")
                        else:
                             logging.error(f"Could not find appropriate stack level for assistant line at indent {current_indent}")
                             level_indent, level_U, existing_A = branch_stack[-1]
                             updated_A_text = (existing_A + "\n" + current_A_text) if existing_A else current_A_text
                             branch_stack[-1] = (level_indent, level_U, updated_A_text)
                             logging.error(f"Fallback: Updated top stack level: {branch_stack[-1]}")

                        if sprite_match:
                            sprite_code = sprite_match.group(1)
                            emotions = self.get_emotions(sprite_code)
                        else:
                            emotions = ['neutral']
                        entry = {
                            'type': 'assistant', 'text': current_A_text,
                            'emotions': emotions,
                            'metadata': current_metadata if not metadata_attached else None
                        }
                        dialogue_entries.append(entry)
                        metadata_attached = True
                        logging.debug(f"Added assistant entry: '{current_A_text}'")

                # Handle end of dialogue block
                elif stripped_line.startswith(('return', 'jump', 'call')):
                    # Check if returning from the initial label/event context
                    if len(branch_stack) <= 1 and current_indent <= (branch_stack[0][0] + 1 if branch_stack else 0):
                         if in_dialogue:
                              logging.debug(f"End of block detected ('{stripped_line}') near root, adding separator.")
                              dialogue_entries.append({"type": "separator"})
                              in_dialogue = False # End the current dialogue context

            except Exception as e:
                logging.exception(f"Error processing line {i} in {filename}: '{line.strip()}' - {str(e)}")

            i += 1

        if in_dialogue and dialogue_entries and dialogue_entries[-1].get("type") != "separator":
             dialogue_entries.append({"type": "separator"})
             logging.debug("Separator added at end of file.")

        logging.info(f"Extracted {len(dialogue_entries)} raw dialogue entries from {filename}")
        return dialogue_entries


    # --- MODIFIED: format_to_chatml (Adds [...] prefix to truncated history) ---
    def format_to_chatml(self, dialogue_entries: List[Dict]) -> List[Dict]:
        """
        Formats dialogue entries into the target ChatML-like structure with history.
        Relies on 'history_context' provided by extract_dialogue.
        Groups consecutive assistant messages.
        Handles missing history context for the turn immediately following the initial message.
        Truncates long assistant messages in the history, adding a [...] prefix.
        """
        formatted_data = []
        if not dialogue_entries:
            return formatted_data

        current_instruction = None
        current_output_lines = []
        current_system_parts = []
        current_history = []
        current_emotions_list = []
        metadata_for_block = None
        first_entry_processed = False
        first_instruction_in_block = None
        first_output_in_block = None
        MAX_HISTORY_LINES = 3 # Max number of lines for assistant history message
        TRUNCATION_PREFIX = "[...] " # Prefix to add when history is truncated


        for i, entry in enumerate(dialogue_entries):
            entry_type = entry.get('type')

            if entry_type == "separator":
                # Finalize the previous block
                if current_instruction is not None:
                    final_output = "\n".join(current_output_lines).strip()
                    if final_output:
                        aggregated_emotions = self.aggregate_emotions(current_emotions_list)
                        if aggregated_emotions and aggregated_emotions != ['neutral']:
                             current_system_parts.append(f"Emotions of the assistant: {aggregated_emotions}")
                        if metadata_for_block and "Metadata =" not in "\n".join(current_system_parts):
                             current_system_parts.insert(0, f"Metadata = {metadata_for_block}")

                        formatted_data.append({
                            "instruction": current_instruction, "input": "",
                            "output": final_output,
                            "system": "\n".join(current_system_parts).strip(),
                            "history": current_history
                        })
                        logging.debug(f"Formatted block added (separator): Instr='{current_instruction[:50]}...', Hist={current_history}")

                # Reset for the next block
                current_instruction = None
                current_output_lines = []
                current_system_parts = []
                current_history = []
                current_emotions_list = []
                metadata_for_block = None
                first_entry_processed = False
                first_instruction_in_block = None
                first_output_in_block = None
                logging.debug("--- Separator Processed ---")
                continue

            if entry_type == 'user':
                # Finalize the previous block
                if current_instruction is not None:
                    final_output = "\n".join(current_output_lines).strip()
                    if final_output:
                        aggregated_emotions = self.aggregate_emotions(current_emotions_list)
                        if aggregated_emotions and aggregated_emotions != ['neutral']:
                             current_system_parts.append(f"Emotions of the assistant: {aggregated_emotions}")
                        if metadata_for_block and "Metadata =" not in "\n".join(current_system_parts):
                             current_system_parts.insert(0, f"Metadata = {metadata_for_block}")

                        if not first_entry_processed:
                             first_instruction_in_block = current_instruction
                             first_output_in_block = final_output
                             logging.debug(f"Stored first turn: U='{first_instruction_in_block[:50]}...', A='{first_output_in_block[:50]}...'")
                             first_entry_processed = True

                        formatted_data.append({
                            "instruction": current_instruction, "input": "",
                            "output": final_output,
                            "system": "\n".join(current_system_parts).strip(),
                            "history": current_history
                        })
                        logging.debug(f"Formatted block added (user): Instr='{current_instruction[:50]}...', Hist={current_history}")


                # Start the new block based on this user entry
                current_instruction = entry["text"]
                history_context = entry.get("history_context")

                # --- HISTORY LOGIC WITH TRUNCATION & PREFIX ---
                history_U = None
                history_A = None # Final (potentially truncated) assistant history message

                # Check if we should use cached first turn history
                if not history_context and first_instruction_in_block and first_output_in_block:
                    history_U = first_instruction_in_block
                    history_A_full = first_output_in_block
                    logging.debug("Using cached first turn for history.")
                    history_A_lines = history_A_full.split('\n')
                    if len(history_A_lines) > MAX_HISTORY_LINES:
                        # Add prefix when truncating
                        history_A = TRUNCATION_PREFIX + "\n".join(history_A_lines[-MAX_HISTORY_LINES:])
                        logging.debug(f"Truncated cached history A from {len(history_A_lines)} to {MAX_HISTORY_LINES} lines.")
                    else:
                        history_A = history_A_full

                # Check if we should use history_context from extract_dialogue
                elif history_context and all(history_context):
                    history_U = history_context[0]
                    history_A_full = history_context[1]
                    history_A_lines = history_A_full.split('\n')
                    if len(history_A_lines) > MAX_HISTORY_LINES:
                        # Add prefix when truncating
                        history_A = TRUNCATION_PREFIX + "\n".join(history_A_lines[-MAX_HISTORY_LINES:])
                        logging.debug(f"Truncated history_context A from {len(history_A_lines)} to {MAX_HISTORY_LINES} lines.")
                    else:
                        history_A = history_A_full
                else:
                    pass # No valid history

                # Assign to current_history if U and A are valid
                if history_U is not None and history_A is not None:
                     current_history = [[history_U, history_A]]
                else:
                     current_history = []
                # --- END HISTORY LOGIC ---


                # Reset parts for the new block
                current_output_lines = []
                current_system_parts = []
                current_emotions_list = []
                metadata_for_block = entry.get('metadata')

                logging.debug(f"User entry processed: Instr='{current_instruction[:50]}...', Hist={current_history}")


            elif entry_type == 'assistant':
                 # Handle case where assistant message appears before any user message
                if not first_entry_processed and current_instruction is None:
                     metadata_for_block = entry.get('metadata')
                     if metadata_for_block:
                         prompt = metadata_for_block.get('prompt')
                         is_random = metadata_for_block.get('random')
                         if prompt: current_instruction = f"What do you have to say about: {prompt}?"
                         elif is_random is True: current_instruction = "*idling*"
                         else: current_instruction = "Please continue."
                     else: current_instruction = "Please continue."
                     logging.debug(f"Assistant first, created default instruction: '{current_instruction}'")
                     current_history = []

                # Append assistant text and collect emotions/metadata
                current_output_lines.append(entry["text"])
                current_emotions_list.append(entry.get('emotions', ['neutral']))

                if metadata_for_block and "Metadata =" not in "\n".join(current_system_parts):
                     current_system_parts.insert(0, f"Metadata = {metadata_for_block}")

                logging.debug(f"Assistant line added: '{entry['text'][:50]}...'")


        # Finalize the very last block
        if current_instruction is not None:
            final_output = "\n".join(current_output_lines).strip()
            if final_output:
                aggregated_emotions = self.aggregate_emotions(current_emotions_list)
                if aggregated_emotions and aggregated_emotions != ['neutral']:
                     current_system_parts.append(f"Emotions of the assistant: {aggregated_emotions}")
                if metadata_for_block and "Metadata =" not in "\n".join(current_system_parts):
                     current_system_parts.insert(0, f"Metadata = {metadata_for_block}")

                if not first_entry_processed:
                     first_instruction_in_block = current_instruction
                     first_output_in_block = final_output
                     logging.debug(f"Stored first turn (end of file): U='{first_instruction_in_block[:50]}...', A='{first_output_in_block[:50]}...'")

                formatted_data.append({
                    "instruction": current_instruction, "input": "",
                    "output": final_output,
                    "system": "\n".join(current_system_parts).strip(),
                    "history": current_history
                })
                logging.debug(f"Final block added: Instr='{current_instruction[:50]}...', Hist={current_history}")

        logging.info(f"Formatted {len(formatted_data)} dialogue blocks.")
        return formatted_data


    # --- aggregate_emotions remains unchanged ---
    def aggregate_emotions(self, emotion_lists: List[List[str]]) -> List[str]:
        """
        Aggregate emotions from multiple consecutive messages into a single emotion set.
        Uses frequency and intensity-based weighting. Returns top 1 or 2 dominant emotions.
        """
        if not emotion_lists: return ['neutral']
        all_emotions = [e for sublist in emotion_lists for e in sublist if e]
        if not all_emotions: return ['neutral']
        emotion_scores = {}
        for emotion in all_emotions:
            intensity = self.EMOTION_INTENSITIES.get(emotion, 1)
            emotion_scores[emotion] = emotion_scores.get(emotion, 0) + intensity
        dominant_emotions = sorted(
            emotion_scores.items(),
            key=lambda item: (item[1], self.EMOTION_INTENSITIES.get(item[0], 1)),
            reverse=True
        )
        if len(dominant_emotions) == 0: return ['neutral']
        elif len(dominant_emotions) == 1: return [dominant_emotions[0][0]]
        else: return [e[0] for e in dominant_emotions[:2]]


    # --- group_dialogue_entries remains unchanged (deprecated) ---
    def group_dialogue_entries(self, entries):
        """DEPRECATED/Integrated: Group consecutive assistant messages together."""
        logging.warning("group_dialogue_entries is deprecated; logic moved to format_to_chatml.")
        return entries


    # --- process_files remains unchanged ---
    def process_files(self, input_files: List[str], output_folder: str):
        """
        Process multiple files with cross-file reference handling.
        Now uses the modified extraction and formatting.
        """
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        files_content = {}
        for input_file in input_files:
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    files_content[input_file] = f.read()
            except Exception as e:
                 logging.error(f"Failed to read input file {input_file}: {e}")
                 continue
        if not files_content:
             logging.error("No input files could be read. Exiting.")
             return []
        logging.info("Starting first pass scan...")
        self.first_pass_scan(files_content)
        logging.info("First pass scan complete.")
        all_dialogues = []
        for input_file, content in files_content.items():
            output_path = os.path.join(
                output_folder,
                os.path.basename(input_file).replace('.rpy', '_dialogue.json')
            )
            logging.info(f"Processing file: {input_file}")
            try:
                dialogue_entries = self.extract_dialogue(content, input_file)
                formatted_data = self.format_to_chatml(dialogue_entries)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(formatted_data, f, indent=2, ensure_ascii=False)
                all_dialogues.extend(formatted_data)
                logging.info(f"Successfully processed {input_file}, found {len(formatted_data)} blocks.")
            except Exception as e:
                logging.exception(f"Error processing {input_file}: {str(e)}")
        return all_dialogues


# --- load_poems_json remains unchanged ---
def load_poems_json(file_path):
    """Read and parse a poems JSON file, ignoring lines starting with '#'."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line for line in f if not line.strip().startswith('#')]
            content = ''.join(lines)
            data = json.loads(content)
            if isinstance(data, list):
                valid_entries = []
                for item in data:
                    if isinstance(item, dict) and "instruction" in item and "output" in item:
                         item.setdefault("input", "")
                         item.setdefault("system", "")
                         item.setdefault("history", [])
                         valid_entries.append(item)
                    else:
                         logging.warning(f"Skipping invalid entry in {file_path}: {item}")
                return valid_entries
            else:
                logging.error(f"Error: Poems file {file_path} does not contain a JSON list.")
                return []
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in {file_path}: {str(e)} at line {e.lineno} col {e.colno}")
        return []
    except FileNotFoundError:
        logging.warning(f"Poems file not found: {file_path}")
        return []
    except Exception as e:
        logging.error(f"Error loading {file_path}: {str(e)}")
        return []


# --- get_name_replacements remains unchanged ---
def get_name_replacements():
    """Prompt the user for replacements for <MONIKA> and <USER>."""
    print("\nPlease provide replacements for standard placeholders.")
    print("Press Enter to keep the default value.")
    monika_name = input("Replace <MONIKA> with (default: <MONIKA>): ").strip() or "<MONIKA>"
    user_name = input("Replace <USER> with (default: <USER>): ").strip() or "<USER>"
    return monika_name, user_name

# --- fix_empty_instructions remains unchanged ---
def fix_empty_instructions(output_folder: str, combined_filename: str):
    """
    Process the final combined JSON file to replace empty or invalid instructions
    with a default instruction. Now operates on the final combined file.
    """
    default_instruction = "What's on your mind?"
    file_path = os.path.join(output_folder, combined_filename)
    if not os.path.exists(file_path):
        logging.error(f"Combined file {file_path} not found for fixing instructions.")
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
        modified = False
        problematic_instructions = {"", ")", "(", " "}
        for entry in data:
            if "instruction" not in entry or entry["instruction"].strip() in problematic_instructions:
                entry["instruction"] = default_instruction
                modified = True
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('[\n')
                for i, entry in enumerate(data):
                    f.write('\t{\n')
                    f.write(f'\t\t"instruction": {json.dumps(entry.get("instruction", default_instruction), ensure_ascii=False)},\n')
                    f.write(f'\t\t"input": {json.dumps(entry.get("input", ""), ensure_ascii=False)},\n')
                    f.write(f'\t\t"output": {json.dumps(entry.get("output", ""), ensure_ascii=False)},\n')
                    f.write(f'\t\t"system": {json.dumps(entry.get("system", ""), ensure_ascii=False)},\n')
                    history_val = entry.get("history", [])
                    if not isinstance(history_val, list): history_val = []
                    f.write(f'\t\t"history": {json.dumps(history_val, ensure_ascii=False)}\n')
                    f.write('\t}')
                    if i < len(data) - 1: f.write(',')
                    f.write('\n')
                f.write(']')
            logging.info(f"Successfully fixed empty/invalid instructions in {combined_filename}")
        else:
            logging.info(f"No empty/invalid instructions found in {combined_filename}")
    except json.JSONDecodeError as e:
         logging.error(f"Error reading JSON from {file_path} during instruction fixing: {e}")
    except Exception as e:
        logging.exception(f"Error processing instructions in {file_path}: {str(e)}")


# --- process_folder remains unchanged ---
def process_folder(input_folder: str, output_folder: str):
    """Process all .rpy files in a folder, combine with poems, apply replacements, and save."""
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    input_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.rpy'): input_files.append(os.path.join(root, file))
    if not input_files:
        logging.error(f"No .rpy files found in {input_folder}. Exiting.")
        return
    extractor = DialogueExtractor()
    all_rpy_dialogues = extractor.process_files(input_files, output_folder)
    poems_dialogues = []
    poems_files = ["My poems.json", "MAS poems.json", "Base game poems.json"]
    for poems_file in poems_files:
        file_path = os.path.join(input_folder, poems_file)
        poems_data = load_poems_json(file_path)
        if poems_data:
             poems_dialogues.extend(poems_data)
             logging.info(f"Loaded {len(poems_data)} entries from {poems_file}")
    all_dialogues = all_rpy_dialogues + poems_dialogues
    logging.info(f"Total dialogue blocks combined: {len(all_dialogues)}")
    if not all_dialogues:
        logging.error("No dialogue entries found after processing RPY files and poems. Cannot proceed.")
        return
    monika_name, user_name = get_name_replacements()
    replacement_count = 0
    for entry in all_dialogues:
        for field in ["instruction", "input", "output", "system"]:
            if field in entry and isinstance(entry[field], str):
                 original_text = entry[field]
                 if monika_name != "<MONIKA>": entry[field] = entry[field].replace("<MONIKA>", monika_name)
                 if user_name != "<USER>": entry[field] = entry[field].replace("<USER>", user_name)
                 if entry[field] != original_text: replacement_count += 1
        if "history" in entry and isinstance(entry["history"], list):
             for turn in entry["history"]:
                 if isinstance(turn, list) and len(turn) == 2:
                     if isinstance(turn[0], str):
                          original_u = turn[0]
                          if user_name != "<USER>": turn[0] = turn[0].replace("<USER>", user_name)
                          if turn[0] != original_u: replacement_count += 1
                     if isinstance(turn[1], str):
                          original_a = turn[1]
                          if monika_name != "<MONIKA>": turn[1] = turn[1].replace("<MONIKA>", monika_name)
                          if turn[1] != original_a: replacement_count += 1
    logging.info(f"Applied name replacements. Approx {replacement_count} replacements made.")
    combined_filename = "MoniDatasetLoRA_Formatted.json"
    combined_output_path = os.path.join(output_folder, combined_filename)
    try:
        with open(combined_output_path, 'w', encoding='utf-8') as f:
            f.write('[\n')
            for i, entry in enumerate(all_dialogues):
                f.write('\t{\n')
                f.write(f'\t\t"instruction": {json.dumps(entry.get("instruction", ""), ensure_ascii=False)},\n')
                f.write(f'\t\t"input": {json.dumps(entry.get("input", ""), ensure_ascii=False)},\n')
                f.write(f'\t\t"output": {json.dumps(entry.get("output", ""), ensure_ascii=False)},\n')
                f.write(f'\t\t"system": {json.dumps(entry.get("system", ""), ensure_ascii=False)},\n')
                history_val = entry.get("history", [])
                if not isinstance(history_val, list): history_val = []
                f.write(f'\t\t"history": {json.dumps(history_val, ensure_ascii=False)}\n')
                f.write('\t}')
                if i < len(all_dialogues) - 1: f.write(',')
                f.write('\n')
            f.write(']')
        logging.info(f"Successfully created combined output with new format at {combined_output_path}")
        fix_empty_instructions(output_folder, combined_filename)
    except Exception as e:
        logging.exception(f"Error during final processing or writing combined file: {str(e)}")


if __name__ == "__main__":
    input_folder = "rpy_files"
    output_folder = "dialogue_output_formatted"
    if not os.path.isdir(input_folder):
        logging.error(f"Input folder '{input_folder}' not found. Please create it and place your files inside.")
    else:
       Path(output_folder).mkdir(parents=True, exist_ok=True)
       logging.info(f"Input folder: '{input_folder}'")
       logging.info(f"Output folder: '{output_folder}'")
       process_folder(input_folder, output_folder)
       logging.info("Processing complete.")
