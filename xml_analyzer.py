import xml.etree.ElementTree as ET
import re
import inspect

#future code -  if tag does not exist then create that tag
#               for example, if you have the color tag, and 32768 and 32769 are present
#               and we are trying to add a new color, the code should dynamically add a
#               new color ID with all the parameters

#               Then i have to ensure that that ID is assigned to the row that needs the 
#               color
#               If a form has not been formatted before, create an id for each cell / member
#               and then insert it into the form formatting tag

#               dataValidationRule, formFormattings ...
#               should be generated, does not get created without any rules
#               dataValidationRule generation should be sensitive about positions

#               What if i inject only the dataValidation rule and the formFormatting for a 
#               particular color? Will that cause the form to generate the other values by itself?
#               Need to ask for an instance where i can try these out...

class XMLAnalyzer:
    def __init__(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        self.INPUT_XML_FILE = ""
        self.safe_header = None
        self.tree = None
        self.root = None

    def get_rowcols(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        # Solves the "Cartesian Product" bug by cross-joining members just like EPM
        if self.root is None:
            return {"rows": [], "columns": []}
            
        def parse_segments(xml_path):
            container_list = []
            parent_node = self.root.find(xml_path)
            if parent_node is None: return []
                
            for segment in parent_node.findall("segment"):
                dim_size = segment.get("size", segment.get("width", segment.get("height", "")))
                
                # Start with a blank combination
                combos = [{}] 
                
                for dimension in segment.findall("dimension"):
                    dim_name = dimension.get("name", "")
                    dim_items = []
                    
                    for child in dimension:
                        if child.tag == "formula":
                            dim_items.append({"name": child.get("label", "Formula"), "type": "FORMULA"})
                        elif child.tag == "function":
                            mbr = child.find("member")
                            # Extract JUST the raw member name for EPM's tuple mapping
                            raw_name = mbr.get("name") if mbr is not None else ""
                            # Keep the full function name hidden in metadata just in case
                            full_func = f"{child.get('name')}({raw_name})"
                            
                            dim_items.append({"name": raw_name, "_debug_name": full_func, "type": "FUNCTION"})
                        elif child.tag == "member":
                            dim_items.append({"name": child.get("name", ""), "type": "MEMBER"})
                            
                    # Multiply out combinations (Cross-Join)
                    if dim_items:
                        new_combos = []
                        for combo in combos:
                            for item in dim_items:
                                new_c = combo.copy()
                                new_c[dim_name] = item["name"] # Store dimension mapping for Tuples!
                                new_c["_display_name"] = item["name"] # The innermost member name
                                new_c["_type"] = item["type"]
                                new_c["_size"] = dim_size
                                new_combos.append(new_c)
                        combos = new_combos
                        
                for c in combos:
                    if c: container_list.append(c)
                    
            return container_list

        return {
            "rows": parse_segments(".//query/rows"),
            "columns": parse_segments(".//query/columns")
        }

    def get_format_map(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        
        format_map = {}
        if self.root is None: return format_map

        # 1. Map Colors and Styles
        colors_dict = {c.get("id"): f"#{int(c.get('R', '0')):02X}{int(c.get('G', '0')):02X}{int(c.get('B', '0')):02X}"
                       for c in self.root.findall(".//values/colors/color")}
        style_to_hex = {}
        
        for style in self.root.findall(".//cellStyles/cellStyle"):
            bg = style.find(".//backColor")
            if bg is not None and bg.get("id") in colors_dict:
                style_to_hex[style.get("id")] = colors_dict[bg.get("id")]

        # 2. Extract DVRs directly to the coordinate map
        for dvr in self.root.findall(".//dataValidationRules/dataValidationRule"):
            try:
                # EPM stores them as floats like "0.0" or "1.0", so convert float -> int
                r_loc = int(float(dvr.get("rowLocation", "0")))
                c_loc = int(float(dvr.get("colLocation", "0")))
                cond = dvr.find("dataValidationCond")
                
                if cond is not None and cond.get("styleId") in style_to_hex:
                    hex_color = style_to_hex[cond.get("styleId")]
                    
                    # Because EPM uses 0 for metadata rows/cols and 1+ for data cells,
                    # and our UI now expects exactly that coordinate system, 
                    # we can just map it directly!
                    format_map[(r_loc, c_loc)] = hex_color
                    
            except ValueError: 
                pass

        return format_map

#not working as of now
    def apply_master_formatting(self):
        # # Get the current frame, then access the code object's name
        # func_name = inspect.currentframe().f_code.co_name
        # print(f"I am currently running inside(2): {func_name}")
        
        # if self.root is None: return False
        # grid_data = self.get_rowcols()
        # print(grid_data)
        
        # self.setup_formatting_foundation()
        # self.ensure_txt_formats()
        
        # dark_blue_id = self.add_new_color("11", "37", "49")
        # light_blue_id = self.add_new_color("240", "248", "255")
        # white_id = self.add_new_color("255", "255", "255")
        # border_ids = self.inject_standard_borders()
        
        # col_style_id = self.add_advanced_cell_style(bg_color_id=dark_blue_id, txt_color_id=white_id, is_bold=True, border_ids=border_ids)
        # row_style_id = self.add_advanced_cell_style(bg_color_id=light_blue_id)

        # # Clean out old "Auto Format Rules" so we start fresh
        # dvr_bucket = self.root.find(".//dataValidationRules")
        # if dvr_bucket is not None:
        #     dvrs_to_remove = [d for d in dvr_bucket.findall("dataValidationRule") if d.get("name") == "Auto Format Rule"]
        #     for d in dvrs_to_remove: dvr_bucket.remove(d)
        
        # print("Cols",grid_data["columns"])
        # print("Rows",grid_data["rows"])
        
        # # Clean out old Tuples so we start fresh
        # tuples_bucket = self.root.find(".//formFormattings/formFormatting/dataCellMbrTuples")
        # if tuples_bucket is not None:
        #     tuples_bucket.clear() # This safely deletes everything inside the tag
            
        # # =========================================================
        # # ENGINE 2: Tuple Mappings (Metadata-Based Data Cells)
        # # =========================================================
        
        # # Loop through every possible row and column combination
        # for row_combo in grid_data["rows"]:
        #     for col_combo in grid_data["columns"]:
                
        #         # Extract the actual dimensions and members, ignoring our '_' metadata keys
        #         row_mbrs = [{"name": val, "dim": key} for key, val in row_combo.items() if not key.startswith("_")]
        #         col_mbrs = [{"name": val, "dim": key} for key, val in col_combo.items() if not key.startswith("_")]
                
        #         # Call the tuple mapper (using your desired style ID)
        #         # If you want to mimic the original file exactly, you'll need logic here 
        #         # to assign specific style IDs to specific row_combo["_display_name"] values.
        #         self.add_tuple_mapping(style_id=col_style_id, row_mbrs=row_mbrs, col_mbrs=col_mbrs)
                
        # print("Successfully injected tuple mapping!")
        
        # # 1. Paint ALL Column Metadata Dark Blue (Using DVR rowLocation=0.0)
        # for c_idx in range(len(grid_data["columns"])):
        #     self.add_location_dvr(row_loc=0.0, col_loc=c_idx+1, style_id=col_style_id, hex_color="0B2531")

        # # 2. Paint ALL Row Metadata Light Blue (Using DVR colLocation=0.0)
        # for r_idx in range(len(grid_data["rows"])):
        #     self.add_location_dvr(row_loc=r_idx+1, col_loc=0.0, style_id=row_style_id, hex_color="F0F8FF")
                
        # # # 3. Paint Formula Data Cells Dark Blue (Optional - targets the specific data cells)
        # # for r_idx, row_dict in enumerate(grid_data["rows"]):
        # #     if row_dict.get("_type") == "FORMULA" or row_dict.get("_size") == "-4":
        # #         for c_idx in range(len(grid_data["columns"])):
        # #             self.add_location_dvr(row_loc=r_idx, col_loc=c_idx, style_id=col_style_id, hex_color="0B2531")

        # self.tree.write(self.INPUT_XML_FILE, encoding="UTF-8", xml_declaration=True)
        # self._restore_header_block()
        # print("Master DVR formatting complete!")
        # return True
        pass

    def apply_master_formatting(self):
            # Get the current frame, then access the code object's name
            func_name = inspect.currentframe().f_code.co_name
            print(f"I am currently running inside(2): {func_name}")
            
            if self.root is None: return False
            grid_data = self.get_rowcols()
            print(grid_data)
            
            self.setup_formatting_foundation()
            self.ensure_txt_formats()
            
            dark_blue_id = self.add_new_color("11", "37", "49")
            light_blue_id = self.add_new_color("240", "248", "255")
            white_id = self.add_new_color("255", "255", "255")
            border_ids = self.inject_standard_borders()
            
            col_style_id = self.add_advanced_cell_style(bg_color_id=dark_blue_id, txt_color_id=white_id, is_bold=True, border_ids=border_ids)
            row_style_id = self.add_advanced_cell_style(bg_color_id=light_blue_id)

            # --- CLEANUP PHASE ---
            # 1. Clean out old "Auto Format Rules" (DVRs) so we start fresh
            dvr_bucket = self.root.find(".//dataValidationRules")
            if dvr_bucket is not None:
                dvrs_to_remove = [d for d in dvr_bucket.findall("dataValidationRule") if d.get("name") == "Auto Format Rule"]
                for d in dvrs_to_remove: dvr_bucket.remove(d)

            # 2. Clean out old Tuple Mappings to ensure data cells have NO formatting
            tuples_bucket = self.root.find(".//formFormattings/formFormatting/dataCellMbrTuples")
            if tuples_bucket is not None:
                tuples_bucket.clear() 
                print("Wiped existing tuple mappings to ensure blank data cells.")

            print("Cols",grid_data["columns"])
            print("Rows",grid_data["rows"])
            
            # =========================================================
            # ENGINE 1: Data Validation Rules (Location-Based Headers)
            # =========================================================
            
            # 1. Paint ALL Column Metadata Dark Blue (Using DVR rowLocation=0.0)
            for c_idx in range(len(grid_data["columns"])):
                self.add_location_dvr(row_loc=0.0, col_loc=c_idx+1, style_id=col_style_id, hex_color="0B2531")

            # 2. Paint ALL Row Metadata Light Blue (Using DVR colLocation=0.0)
            for r_idx in range(len(grid_data["rows"])):
                self.add_location_dvr(row_loc=r_idx+1, col_loc=0.0, style_id=row_style_id, hex_color="F0F8FF")

            # ENGINE 2 (Tuple Mappings) has been removed. Data cells will remain unformatted.

            self.tree.write(self.INPUT_XML_FILE, encoding="UTF-8", xml_declaration=True)
            self._restore_header_block()
            print("Master DVR formatting complete! (Data cells left unformatted)")
            return True

    def add_tuple_mapping(self, style_id, row_mbrs, col_mbrs):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        # The new engine to physically inject the metadata mappings
        tuples_container = self.root.find(".//formFormattings/formFormatting/dataCellMbrTuples")
        if tuples_container is None: return

        new_tuple = ET.SubElement(tuples_container, "dataCellMbrTuple")
        ET.SubElement(new_tuple, "cellStyleId").text = str(style_id)

        row_frm = ET.SubElement(new_tuple, "frmMbrTuple")
        ET.SubElement(row_frm, "gridLocation").text = "rows"
        for mbr in row_mbrs:
            ET.SubElement(row_frm, "mbr", name=mbr["name"], segment=f"{style_id}.0", dim=mbr["dim"])

        col_frm = ET.SubElement(new_tuple, "frmMbrTuple")
        ET.SubElement(col_frm, "gridLocation").text = "columns"
        for mbr in col_mbrs:
            ET.SubElement(col_frm, "mbr", name=mbr["name"], segment=f"{style_id}.0", dim=mbr["dim"])
    
    def load_file(self, filepath):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        """Loads the XML file and extracts the safe header block."""
        self.INPUT_XML_FILE = filepath
        self.safe_header = self._extract_header_block(filepath)
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        print(f"File loaded: {filepath}")

    def _extract_header_block(self, filepath):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        """
        Opens the file as plain text.
        Captures everything from the start of <form...> down to the end of </pipPrefs>.
        Stores it in RAM.
        """
        with open(filepath, "r", encoding="UTF-8") as f:
            content = f.read()

        # Regex Explanation:
        # (?s)      -> Dot matches newline (treat file as one long string)
        # <form     -> Find the literal start of the form tag
        # .*?       -> Match everything in between (non-greedy)
        # </pipPrefs> -> Stop exactly at the closing pipPrefs tag
        pattern = r"(?s)(<form.*?</pipPrefs>)"
        
        match = re.search(pattern, content)
        
        if match:
            print("Header block successfully captured to RAM.")
            return match.group(1) # This is the "Safe" string
        else:
            raise ValueError("Could not find the <form>...<pipPrefs> block in the source file.")

    def _restore_header_block(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        """
        Opens the modified (messy) file.
        Finds the SAME block (which is now formatted badly).
        Overwrites it with the 'original_block' from RAM.
        """
        filepath = self.INPUT_XML_FILE
        original_block = self.safe_header

        with open(filepath, "r", encoding="UTF-8") as f:
            new_content = f.read()

        # We use the same pattern to find the "Messy" version in the new file
        pattern = r"(?s)(<form.*?(?:</pipPrefs>|<pipPrefs\s*/>))"
        
        # Check if the pattern exists before trying to replace
        if not re.search(pattern, new_content):
            print("Warning: Could not find the target block in the new file. Replacement skipped.")
            return

        # The Swap: Replace the found 'messy' chunk with the 'clean' original chunk
        final_content = re.sub(pattern, lambda m: original_block, new_content, count=1)
        
        # Write the result back to disk
        with open(filepath, "w", encoding="UTF-8") as f:
            f.write(final_content)
            
        print("Surgical restoration complete: Header formatting restored.")

    def get_format_rows(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        
        if self.root is None:
            return []
            
        rows_data = []
        
        # 1. Find the main container
        tuples_container = self.root.find(".//formFormattings/formFormatting/dataCellMbrTuples")
        
        if tuples_container is not None:
            # 2. Loop through each block
            for data_tuple in tuples_container.findall("dataCellMbrTuple"):
                
                # Create a dictionary to hold this block's data together
                tuple_dict = {
                    "style_id": "None",
                    "members": []
                }
                
                # 3. Get the Style ID
                style_node = data_tuple.find("cellStyleId")
                if style_node is not None:
                    tuple_dict["style_id"] = style_node.text
                
                # 4. Loop through ALL frmMbrTuple tags inside this block
                for frm_mbr in data_tuple.findall("frmMbrTuple"):
                    
                    # 5. Grab the gridLocation text ("rows" or "columns")
                    loc_node = frm_mbr.find("gridLocation")
                    grid_loc = loc_node.text if loc_node is not None else "None"
                    
                    # 6. Grab the member attributes
                    mbr_node = frm_mbr.find("mbr")
                    if mbr_node is not None:
                        mbr_info = {
                            "location": grid_loc,
                            "name": mbr_node.get("name"),
                            "segment": mbr_node.get("segment"),
                            "dim": mbr_node.get("dim") # Grabbing dim as well since it's there
                        }
                        # Add this member to our block
                        tuple_dict["members"].append(mbr_info)
                        
                # Add the fully assembled block to our main list
                rows_data.append(tuple_dict)
                        
        return rows_data
    
    def get_colors(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        # SAFETY CHECK
        if self.root is None:
            return []
            
        color_data = []
        colors = self.root.find(".//values/colors")
        
        if colors is not None:
            for color in colors.findall("color"):
                color_id = color.get("id")
                # Add safety if attributes are missing
                r = color.get("R", "0")
                g = color.get("G", "0")
                b = color.get("B", "0")
                rgb_values = [r, g, b]
                
                hex_val = self.rgb_to_hex(rgb_values)
                color_data.append((color_id, hex_val))
            
        return color_data

    def inject_colors(self, color_list):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        if self.root == None:
            print("No file loaded.")
            return

        color_map = {str(id_data): color_data for id_data, color_data in color_list}
        colors = self.root.find(".//values/colors")  
         
        updates_made = False
        if colors is not None:
            for color in colors.findall("color"):
                xml_id = str(color.get("id"))
                
                if xml_id in color_map:
                    hex_value = color_map[xml_id]
                    rgb_list = self.hex_to_rgb([hex_value])
                    
                    old_rgb_color = [color.get("R"), color.get("G"), color.get("B")]
                    
                    color.set("R", str(rgb_list[0][0]))
                    color.set("G", str(rgb_list[0][1]))
                    color.set("B", str(rgb_list[0][2]))
                    
                    print(f"Updated ID: {xml_id} from : {old_rgb_color} ==> to : {rgb_list[0]}")
                    updates_made = True

        if updates_made:
            print("Writing changes to file...")
            self.tree.write(self.INPUT_XML_FILE, encoding="UTF-8", xml_declaration=True)
            
            print("Restoring original header formatting...")
            self._restore_header_block()
            print("Done.")
        else:
            print("No matching IDs found. File was not touched.")

    def setup_formatting_foundation(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        #do it one by one, start simple
        #future code -  check if the form already has formatting rules applied.
        #               we look inside dataCellMbrTuples. if there are items, we 
        #               leave the structure alone. if it is empty or missing, 
        #               we build the blank buckets from scratch.

        if self.root is None:
            print("No file loaded.")
            return False

        ff_parent = self.root.find(".//formFormattings")
        if ff_parent is None:
            ff_parent = ET.SubElement(self.root, "formFormattings")

        ff = ff_parent.find("formFormatting")
        if ff is None:
            ff = ET.SubElement(ff_parent, "formFormatting", designTime="true", userName="[CURRENT_USER]", displayOptions="-2147483646")

        # Check if rules already exist
        tuples = ff.find("dataCellMbrTuples")
        if tuples is not None and len(list(tuples)) > 0:
            print("Status: Form already contains formatting. Preserving existing rules.")
            return True # True means it was already formatted

        print("Status: Form is blank. Building base XML structure...")
        
        # Build the empty buckets if they don't exist
        for bucket in ["dataCellMbrTuples", "cellStyles", "columnRowSizes"]:
            if ff.find(bucket) is None:
                ET.SubElement(ff, bucket)

        values = ff.find("values")
        if values is None:
            values = ET.SubElement(ff, "values")
            txt_frmts = ET.SubElement(values, "txtFrmts")
            ET.SubElement(txt_frmts, "txtFrmt", id="1").text = "Bold"
            ET.SubElement(txt_frmts, "txtFrmt", id="2").text = "Underline"
            ET.SubElement(txt_frmts, "txtFrmt", id="3").text = "StrikeThrough"
            
            # Colors correctly belongs in <values>
            ET.SubElement(values, "colors")

        objs = ff.find("objs")
        if objs is None:
            objs = ET.SubElement(ff, "objs")
            
            # numFrmts and borders correctly belong in <objs>
            ET.SubElement(objs, "numFrmts")
            ET.SubElement(objs, "borders")

        return False # False means it was blank and we just built it

    def ensure_txt_formats(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        #do it one by one, start simple
        #future code -  Even if the form already has formatting, the txtFrmts bucket 
        #               might be empty. We must forcefully ensure 0, 1, 2, and 3 exist 
        #               so our advanced cell styles can use them.
        
        txt_bucket = self.root.find(".//formFormattings/formFormatting/values/txtFrmts")
        
        if txt_bucket is not None:
            formats = {"0": "Italic", "1": "Bold", "2": "Underline", "3": "StrikeThrough"}
            
            for f_id, f_text in formats.items():
                # Only add if it doesn't already exist
                if txt_bucket.find(f"txtFrmt[@id='{f_id}']") is None:
                    txt = ET.SubElement(txt_bucket, "txtFrmt", id=f_id)
                    txt.text = f_text
            print("Verified standard text formats (Bold, Italic, etc) are present.")

    def get_next_available_id(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        #do it one by one, start simple
        #future code -  scans the entire formFormatting tag for any existing IDs.
        #               It must check BOTH attributes (id="123") AND child tags (<id>123</id>)
        #               because Oracle EPM is inconsistent with how it stores them.
        
        highest_id = 32767
        
        if self.root is not None:
            ff_node = self.root.find(".//formFormattings/formFormatting")
            if ff_node is not None:
                
                # 1. Search for attributes (e.g., <color id="32768"> or <cellStyle id="32769">)
                for elem in ff_node.findall(".//*[@id]"):
                    try:
                        current_id = int(elem.get("id"))
                        highest_id = max(highest_id, current_id)
                    except ValueError:
                        pass 
                
                # 2. Search for child tags (e.g., <border><id>32770</id></border>)
                for elem in ff_node.findall(".//id"):
                    try:
                        if elem.text:
                            current_id = int(elem.text.strip())
                            highest_id = max(highest_id, current_id)
                    except ValueError:
                        pass
                        
        return highest_id + 1

#working fine
    def add_new_color(self, r, g, b):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        #future code -  dynamically generates a safe ID, creates the color tag, 
        #               and returns the new ID so other functions can link to it.
        
        new_id = self.get_next_available_id()
        colors_bucket = self.root.find(".//formFormattings/formFormatting/values/colors")
        
        if colors_bucket is not None:
            new_color = ET.SubElement(colors_bucket, "color")
            new_color.set("id", str(new_id))
            new_color.set("R", str(r))
            new_color.set("G", str(g))
            new_color.set("B", str(b))
            print(f"Added new color ID: {new_id} ({r},{g},{b})")
            return new_id
        else:
            print("Error: Could not find <colors> bucket.")
            return None

#works as intended, but hardcoded
    def inject_standard_borders(self):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")

        # 1. Define your exact hardcoded XML string
        hardcoded_xml = """
        <borders>
            <border>
                <id>32768</id>
                <color R="255" G="255" B="255" />
                <placement>Top</placement>
                <style>solid</style>
                <width>0.4</width>
            </border>
            <border>
                <id>32769</id>
                <color R="255" G="255" B="255" />
                <placement>Right</placement>
                <style>solid</style>
                <width>0.4</width>
            </border>
            <border>
                <id>32770</id>
                <color R="255" G="255" B="255" />
                <placement>Bottom</placement>
                <style>solid</style>
                <width>0.4</width>
            </border>
            <border>
                <id>32771</id>
                <color R="255" G="255" B="255" />
                <placement>Left</placement>
                <style>solid</style>
                <width>0.4</width>
            </border>
        </borders>
        """

        # 2. Parse the hardcoded string into ElementTree objects
        new_borders_element = ET.fromstring(hardcoded_xml)

        # 3. Brute-force search to find the existing borders tag
        # Using .iter() and checking the string ignores all namespace headaches
        for elem in self.root.iter():
            if 'borders' in elem.tag.lower():
                
                # Wipe out anything currently inside the existing <borders/> tag
                elem.clear() 
                
                # Inject all the hardcoded <border> children into the tag
                for new_border in new_borders_element:
                    elem.append(new_border)
                
                print("Hardcoded borders injected successfully!")
                
                # Return the hardcoded IDs you provided
                return [32768, 32769, 32770, 32771]

        # If this loop finishes without returning, the tag literally isn't in the tree
        print("Error: Could not find any tag containing 'borders' in the XML tree.")
        return []

#does not work as intended, will have to go through later
    def add_advanced_cell_style(self, bg_color_id, txt_color_id=None, is_bold=False, border_ids=None):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        #future code -  generates a dynamic style ID, links the background, text, 
        #               and border IDs, and returns the new style ID for the DVR.
        
        style_id = self.get_next_available_id()
        styles_bucket = self.root.find(".//formFormattings/formFormatting/cellStyles")
        
        if styles_bucket is not None:
            cell_style = ET.SubElement(styles_bucket, "cellStyle", id=str(style_id))
            
            # --- OBJS (Borders) ---
            objs_node = ET.SubElement(cell_style, "objs")
            if border_ids:
                for b_id in border_ids:
                    ET.SubElement(objs_node, "obj", type="border", id=str(b_id))
            
            # --- VALUES ---
            values_node = ET.SubElement(cell_style, "cellStyleValues")
            ET.SubElement(values_node, "font", id="32768") # Standard Arial font Oracle always defaults to
            ET.SubElement(values_node, "readOnly").text = "false"
            ET.SubElement(values_node, "backColor", id=str(bg_color_id))
            
            if txt_color_id:
                ET.SubElement(values_node, "txtColor", id=str(txt_color_id))
                
            ET.SubElement(values_node, "wordWrap").text = "false"
            
            if is_bold:
                ET.SubElement(values_node, "format", id="1") # 1 = Bold
                
            print(f"Added advanced cellStyle ID: {style_id}")
            return style_id
        return None

#working fine
    def add_location_dvr(self, row_loc, col_loc, style_id, hex_color):
        # Get the current frame, then access the code object's name
        func_name = inspect.currentframe().f_code.co_name
        print(f"I am currently running inside: {func_name}")
        #future code -  creates a DVR linking grid coordinates to the dynamically generated style ID.
        
        clean_hex = hex_color.replace("#", "")
        decimal_color = str(int(clean_hex, 16))
        
        dvr_bucket = self.root.find(".//dataValidationRules")
        if dvr_bucket is None:
            print("Error: <dataValidationRules> not found.")
            return
            
        rule = ET.SubElement(dvr_bucket, "dataValidationRule")
        rule.set("position", "1")
        rule.set("name", "Auto Format Rule")
        rule.set("enabled", "true")
        rule.set("customStyle", "true")
        rule.set("description", "This was auto-generated by the XML Analyzer. It links a specific cell/row/column to a formatting style.")
        rule.set("rowLocation", str(float(row_loc)))
        rule.set("colLocation", str(float(col_loc)))
        
        cond = ET.SubElement(rule, "dataValidationCond")
        cond.set("toolTip", "")
        cond.set("groupOpenNestingLevel", "0")
        cond.set("operator", "0")
        cond.set("displayMessageInDVPane", "false")
        cond.set("honorPmRules", "false")
        cond.set("negate", "false")
        cond.set("groupCloseNestingLevel", "0")
        cond.set("position", "1")
        cond.set("styleId", str(style_id))
        cond.set("type", "8") # 8 = Location Based Rule
        cond.set("bgColor", decimal_color)
        cond.set("Valid", "true")
        cond.set("logicalOperator", "0")
        
        ET.SubElement(cond, "compareValue", type="6", value="")
        ET.SubElement(cond, "compareToValue", type="0", value="")
        
        print(f"Added DVR for Row {row_loc}, Col {col_loc} mapping to Style {style_id}")
    
    @staticmethod
    def rgb_to_hex(color_list):
        hex_val = f"{int(color_list[0]):02X}{int(color_list[1]):02X}{int(color_list[2]):02X}"
        return hex_val.upper()

    @staticmethod
    def hex_to_rgb(color_list):
        return_color_list = []
        for hex_str in color_list:
            # SAFETY FIX: Remove '#' if present
            clean_hex = hex_str.replace("#", "")
            
            # Now slice the clean string
            r = int(clean_hex[0:2], 16)
            g = int(clean_hex[2:4], 16)
            b = int(clean_hex[4:6], 16)
            
            return_color_list.append([str(r), str(g), str(b)])
        return return_color_list