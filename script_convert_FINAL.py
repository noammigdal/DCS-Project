def process_command(command):
    parts = command.strip().split()

    if not parts:
        return None

    opcode = None
    result = ""

    if parts[0] == "inc_lcd":
        opcode = "01"
        result = opcode + format(int(parts[1]), '02X')  # Convert to uppercase hex

    elif parts[0] == "dec_lcd":
        opcode = "02"
        result = opcode + format(int(parts[1]), '02X')  # Convert to uppercase hex

    elif parts[0] == "rra_lcd":
        opcode = "03"
        result = opcode + format(ord(parts[1]), '02X')  # Convert to uppercase hex

    elif parts[0] == "set_delay":
        opcode = "04"
        result = opcode + format(int(parts[1]), '02X')  # Convert to uppercase hex

    elif parts[0] == "clear_lcd" or parts[0] == "clear_all_leds":
        opcode = "05"
        result = opcode

    elif parts[0] == "stepper_deg":
        opcode = "06"
        result = opcode + format(int(parts[1]), '02X')  # Convert to uppercase hex

    elif parts[0] == "stepper_scan":
        opcode = "07"
        l_r_parts = parts[1].split(',')  # Split the l and r values by comma
        result = opcode + format(int(l_r_parts[0]), '02X') + format(int(l_r_parts[1]), '02X')  # Convert to uppercase hex

    elif parts[0] == "sleep":
        opcode = "08"
        result = opcode

    return result

def convert_file(input_filename, output_filename):
    with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
        for line in infile:
            hex_command = process_command(line)
            if hex_command:
                outfile.write(hex_command + '\n')

if __name__ == "__main__":
    # Specify your input and output file paths here
    input_filename = 'input.txt'   # Replace with the actual path if needed
    output_filename = 'output.txt'  # Replace with the actual path if needed

    convert_file(input_filename, output_filename)
    print(f"Conversion complete. Output saved to {output_filename}.")
