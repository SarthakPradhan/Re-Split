"""
Author: Sarthak Pradhan
Date: 04/04/2023
Description: function to scan and bill and create elements that can be put into buckets for the convenience of splitting
"""
import re
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Combobox

import cv2
import pandas as pd
import pytesseract

# Load the Tesseract OCR engine
pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR\tesseract.exe"  # path to Tesseract OCR executable

class resplit_App():
    def __init__(self,root):
        self.root = root
        self.root.title("Bill Split root")
        self.root.geometry('700x350')

        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        self.bill_elements = pd.DataFrame()
        # Initialize dictionary to store ocr text results
        self.result_dict = {}

        self.label = Label(self.main_frame, text="Click the button to upload an image", font=('bold', 12), pady=20)
        self.label.grid(row=0, column=0, sticky=W)

        self.button = Button(self.main_frame, text="Upload Image", command=self.open_image)
        self.button.grid(row=1, column=0, sticky=W)

        # Create a StringVar to store the selected value
        self.selected_value_no_users = StringVar()
        # Create a Combobox with some values
        self.combobox = Combobox(self.main_frame, textvariable=self.selected_value_no_users, values=["2", "3", "4"])
        self.combobox.grid(row=2, column=0, sticky=W)
        # Set the default value
        self.combobox.set("2")

        

        # Bind the event for selection change
        self.combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

        # Number of users

        billsplitbutton = Button(self.main_frame, text="Split", command=self.open_bill_split_window)
        billsplitbutton.grid(row=3, column=0, sticky=W)
        # button.pack()

    def open_image(self):
        # Open a file dialog to choose an image file
        file_path = filedialog.askopenfilename()
        if file_path:
            image = cv2.imread(file_path)
            self.process_image(image)
    # Function to handle selection change
    def on_combobox_select(self,event):
        self.selected_option = self.combobox.get()
        print("Selected option:", self.selected_option)

    def run(self):
        # Start the GUI event loop
        self.root.mainloop()


    def open_bill_split_window(self):
        self.root.withdraw()

        self.bill_elements['state'] = False
        
        # print(bill_elements)

        self.no_users = int(self.combobox.get())

        new_window = bill_split_window(self.no_users,self.root,self.result_dict)

    def process_image(self,image):
        # Perform image processing on the uploaded image
        self.image = image
        self.image = ~self.image
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # Rest of the image processing code

        # Perform OCR using Tesseract
        my_config = r"--psm 6 oem 3"
        text = pytesseract.image_to_string(self.gray, config=my_config)

        # Extract text and return the result as a dictionary
        lines = text.split('\n')
        pricePattern = r'([0-9]+\.[0-9]+)'

        # Loop through each line of text and filter out line items
        for row in text.split('\n'):
            if re.search(pricePattern, row) is not None:
                break
            else:
                lines.remove(row)
        lines = list(filter(None, lines))
        pattern = r"^(.*?)\s+\$?([\d.]+)"

        

        # Loop through input list
        for item in lines:
            # Search for pattern in item
            try:
                match = re.search(pattern, item)
                if match:
                    text = match.group(1)
                    if "." in match.group(2):
                        # If the string contains a dot, it's a float
                        number = float(match.group(2))
                    else:
                        # If the string doesn't contain a dot, it's an integer
                        number = int(match.group(2)) / 100
                    self.result_dict[text] = number
            except Exception:
                pass

        # Return the resulting dictionary
        #print(self.result_dict)
        self.result_dict = pd.DataFrame(list(self.result_dict.items()), columns=['Item', 'Price'])
        self.result_dict['copy_index'] = self.result_dict.index
        self.result_dict['state'] = False
        #print(self.result_dict)



class bill_split_window():
    
    def __init__(self,no_users,root,bill_elements):
        self.root = root
        self.bill_elements = bill_elements
        self.bill_elements['state'] = False
        self.root.withdraw()
        print('inside new class', self.bill_elements)
        self.no_users = no_users
        
        self.each_user_items = []
        self.each_user_items_listbox = [None] * no_users
        self.each_user_items_label_total = [None] * no_users

        for j in range(self.no_users):
            self.each_user_items.append(pd.DataFrame(columns=['Item', 'Price', 'copy_index']))

        '''All GUI elements of bill split window start'''
        self.page2_window = Toplevel(self.root)
        # close window and reopen main window when cross button is clicked
        self.page2_window.protocol('WM_DELETE_WINDOW', lambda: self.close_new_window(self.page2_window))

        self.bill_elements_list_box = Listbox(self.page2_window, border=3)
        self.update_bill_gui()
        self.bill_elements_list_box.place(relheight=0.3, relwidth=0.3)


        self.bill_elements_list_box.bind("<<ListboxSelect>>", self.on_main_listbox_select)

        for i in range(no_users):
            self.each_user_items_listbox[i] = Listbox(self.page2_window, border=1)
            self.each_user_items_listbox[i].bind("<<ListboxSelect>>", self.on_user_listbox_select)
            self.each_user_items_label_total[i] = Label(self.page2_window, text="$")
            # parts_list.grid(row=3, column=0, columnspan=3, rowspan=6, pady=20, padx=20)
            self.each_user_items_listbox[i].pack(padx=5, pady=15, side=LEFT)
            self.each_user_items_label_total[i].place(in_=self.each_user_items_listbox[i], relx=0, x=0, rely=1)

        self.page2_window.title("Split Bill among users")
        self.page2_window.geometry('1000x500')
        '''All GUI elements of bill split window end'''

        

        page2_label = Label(self.page2_window, text="Bill Split")
        page2_label.pack()
        page2_btn = Button(self.page2_window, text="Back", command=lambda: self.close_new_window(self.page2_window))
        page2_btn.pack()


    def update_bill_gui(self):
        
        self.bill_elements_list_box.delete(0, END)

        for index, row in self.bill_elements.iterrows():

            self.bill_elements_list_box.insert(int(row["copy_index"]),
                                        str(index) + ") " + str(row["Item"]) + "-$" + str(row["Price"]))
            if row["state"] == True:
                self.bill_elements_list_box.itemconfig(END, fg='gray')
                pass

    def update_user_bill_gui(self):

        for j in range(self.no_users):
            self.each_user_items_listbox[j].delete(0, END)
            for index, row in self.each_user_items[j].iterrows():
                self.each_user_items_listbox[j].insert(END, str(row["Item"]) + "-$" + str(row["Price"]))
            self.each_user_items_label_total[j]["text"] = "Total $" + str(sum(self.each_user_items[j]["Price"].values))

    def close_new_window(self,window):
            # Function to close the new window and show the main window
        window.destroy()
        self.root.deiconify()  # Show the main window

    def on_main_listbox_select(self,event):
        # Function to handle Listbox selection
        try:
            if self.bill_elements.loc[[self.bill_elements_list_box.curselection()[0]]]['state'].values == False:
                self.show_checkboxes()
        except:
            pass

    def on_user_listbox_select(self,event):


        # Function to handle Listbox selection
        index = event.widget.curselection()[0]
        item = event.widget.get(index)
        #print(index)
        #print(int(str(event.widget)[-1]) - 2)
        index_df = int(str(event.widget)[-1]) - 2  # index of the list of user dataframes
        org_index = self.each_user_items[index_df].iloc[[index]]["copy_index"].values[0]
        print('org_index', org_index)
        for j in range(len(self.each_user_items)):
            self.each_user_items[j] = self.each_user_items[j][self.each_user_items[j]["copy_index"] != org_index]
        self.bill_elements.loc[[org_index], ['state']] = False
        self.update_user_bill_gui()
        self.update_bill_gui()


    def show_checkboxes(self):
            selected_list_index = self.bill_elements_list_box.curselection()

            selected_list_element = self.bill_elements_list_box.get(selected_list_index)
            #print(selected_list_element)
            #print(selected_list_index)
            # Create four checkboxes
            checkbox_window = Toplevel(root)
            checkbox_window.title(f"Checkboxes for {selected_list_element}")
            
            chkbox = [None] * self.no_users
            chk_var = [None] * self.no_users
            for i in range(self.no_users):
                chk_var[i] = IntVar()

                chkbox[i] = Checkbutton(checkbox_window, text="User" + str(i + 1), variable=chk_var[i])

                chkbox[i].pack()

            def submit():

                #print(bill_elements)
                # Function to retrieve selected checkboxes' values
                selected_checkboxes = []
                #print(bill_elements.loc[[selected_list_index[0]]])
                for i in range(self.no_users):
                    if chk_var[i].get() == 1:
                        selected_checkboxes.append(i)

                # Show messagebox with selected checkboxes' values

                for i in selected_checkboxes:

                    
                    
                    self.each_user_items[i] = pd.concat([self.each_user_items[i],
                                                    
                                                    pd.DataFrame([[self.bill_elements.loc[[selected_list_index[0]]]["Item"].values[0],
                                  self.bill_elements.loc[[selected_list_index[0]]]["Price"].values[0] / len(
                             selected_checkboxes),
                             self.bill_elements.loc[[selected_list_index[0]]]["copy_index"].values[0]
                             ]],columns=['Item', 'Price', 'copy_index'])
                                                    
                                                    ],ignore_index=True)
                    
                    
                    

                self.update_user_bill_gui()
                self.bill_elements.loc[[selected_list_index[0]], ['state']] = True
                #print("update df", self.bill_elements)
                self.update_bill_gui()
                # print(selected_checkboxes)
                # print("0 frame")
                # print(each_user_items[0])
                # print("1 frame")
                # print(each_user_items[1])
                checkbox_window.destroy()

            submit_button = Button(checkbox_window, text="Submit", command=submit)
            submit_button.pack()


if __name__ == "__main__":
    root = Tk()
    app = resplit_App(root)
    app.run()
