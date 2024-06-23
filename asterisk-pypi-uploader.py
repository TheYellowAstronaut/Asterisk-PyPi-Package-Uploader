import os
import shutil
import subprocess
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import sv_ttk
from PIL import ImageTk, Image

root = Tk()
root.title("Asterisk PyPi Package Uploader")
root.iconbitmap(os.path.join(os.path.dirname(__file__), "config/icon.ico"))

def new_package():
    def browse_files():
        global file_paths
        file_paths = filedialog.askopenfilenames(title="Select Python Files", filetypes=[("Python Files", "*.py")])

    def add_placeholder(entry, placeholder):
        entry.insert(0, placeholder)

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, 'end')

        def on_focus_out(event):
            if entry.get() == '':
                entry.insert(0, placeholder)

        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    title_frame = Frame(root)
    title_frame.pack(side=TOP, pady=10)

    title_icon = Label(title_frame, text="", font=(60))
    title_icon.pack(side=TOP)

    title = Label(title_frame, text="Asterisk PyPi Package Uploader", font=(15))
    title.pack(side=BOTTOM)

    info_frame = Frame(root)
    info_frame.pack(padx=10, pady=10)
    
    img_frame = Frame(info_frame)
    img_frame.pack(side=LEFT, fill=BOTH)

    img = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(__file__), 'config/icon.png')))
    panel = Label(img_frame, image=img)
    panel.image = img
    panel.pack(anchor=CENTER)

    entry_frame = Frame(info_frame)
    entry_frame.pack(side=RIGHT)

    fields = [
        "Enter package name",
        "Enter package description",
        "Enter package version",
        "Enter package requirements (comma-separated)",
        "Enter author name",
        "Enter author email",
        "Enter PyPi username",
        "Enter PyPi password/token"
    ]

    entries = []
    for placeholder in fields:
        entry = ttk.Entry(entry_frame, width=50)
        entry.pack(padx=5, pady=5)
        add_placeholder(entry, placeholder)
        entries.append(entry)

    browse_button = ttk.Button(entry_frame, text="Browse", command=browse_files)
    browse_button.pack(padx=5, pady=5)

    output_text = Text(root, height=10, width=80)
    output_text.pack(padx=10, pady=10)

    madeby_frame = Frame(root)
    madeby_frame.pack(side=BOTTOM, pady=10)

    madeby = Label(madeby_frame, text="Made with 💻 by")
    madeby.pack(side=LEFT)

    tya = Label(madeby_frame, text="TheYellowAstronaut", fg="#fec104", cursor="hand2")
    tya.bind("<Button-1>", lambda e: os.startfile("https://www.youtube.com/channel/UChO2jYK1J2C8qSpA1osSXUg"))
    tya.pack(side=RIGHT)

    def package_upload():
        package_name = entries[0].get()
        package_description = entries[1].get()
        package_version = entries[2].get()
        package_requirements = entries[3].get()
        package_author = entries[4].get()
        author_email = entries[5].get()
        pypi_username = entries[6].get()
        pypi_password = entries[7].get()

        package_dir = os.path.join(os.path.dirname(__file__), "packages/", package_name)
        os.makedirs(package_dir, exist_ok=True)

        for file_path in file_paths:
            shutil.copy(file_path, package_dir)

        setup_file = os.path.join(package_dir, "setup.py")
        readme_file = os.path.join(package_dir, "README.md")

        with open(setup_file, "w") as f:
            f.write(f"""from setuptools import setup, find_packages

setup(
    name='{package_name}',
    version='{package_version}',
    packages=find_packages(),
    install_requires=[{package_requirements}],
    description='{package_description}',
    author='{package_author}',
    author_email='{author_email}',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
    """)

        with open(readme_file, "w") as f:
            f.write(f"# {package_name}\n\n{package_description}")

        def run_command(command):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            for line in process.stdout:
                output_text.insert(END, line)
                output_text.see(END)
            for line in process.stderr:
                output_text.insert(END, line)
                output_text.see(END)
            process.stdout.close()
            process.stderr.close()
            process.wait()
            return process.returncode

        output_text.insert(END, "Building package...\n")
        build_command = f"cd {package_dir} && python setup.py sdist bdist_wheel"
        if run_command(build_command) != 0:
            messagebox.showerror("Error", "Failed to build the package.")
            return

        output_text.insert(END, "Uploading package to PyPi...\n")
        upload_command = f"python -m twine upload -u {pypi_username} -p {pypi_password} {package_dir}/dist/*"
        if run_command(upload_command) != 0:
            messagebox.showerror("Error", "Failed to upload the package to PyPi.")
            return

        output_text.insert(END, "Package uploaded successfully!\n")
        messagebox.showinfo("Success", "Package uploaded successfully!")

    next_button = ttk.Button(root, text="Next", command=package_upload, style="Accent.TButton")
    next_button.pack(padx=10, pady=10)

new_package()

sv_ttk.set_theme("dark")

root.mainloop()
