# WAS Text Nodes - Minimal Extract

A lightweight extract from [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui) containing two text utility nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

## Included Nodes

### Text Multiline
A simple multiline text input node. Any line beginning with `#` is treated as a comment and stripped from the output, making it easy to annotate your prompts without affecting generation.

### Text Load Line From File
Reads lines from a text file (or an inline multiline string) one at a time, with two selection modes:

- **automatic** - advances through lines sequentially across executions, wrapping back to the start when the end is reached.
- **index** - returns the line at a specific index on demand.

Progress is persisted to a local JSON database (`was_suite_settings.json`) so the position survives restarts. File paths are also recorded in a history database (`was_history.json`).

## Installation

1. Clone this repo into your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/RiverSide71/WAS-Text-Nodes
   ```
2. Restart ComfyUI. The nodes will appear under **WAS Suite / Text** in the node browser.

## Requirements

- ComfyUI (any recent version)
- No additional Python dependencies beyond the ComfyUI standard environment

## Credits

Extracted from [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui) by WASasquatch. Original code is MIT licensed - see that repository for the full license text.
"# WAS-text-nodes" 
