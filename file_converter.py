# ➡️ Streamlit ek tool hai jo Python ke programs ko website jaisa banane ke liye use hota hai.
import streamlit as st # type: ignore 

# ➡️ Pandas ek tool hai jo data ko samajhne aur manage karne ke liye use hota hai.
import pandas as pd


# ➡️ BytesIO ek tool hai jo files (jaise CSV ya Excel) ko temporarily memory mein rakhne ke liye use hota hai.
from io import BytesIO

st.set_page_config(page_title="File Converter", layout="wide")

st.sidebar.title("Navigation")

st.sidebar.write("Use the tabs below to navigate through different functionalities.")

tab1, tab2 = st.tabs(["File Upload", "File Processing"])



with tab1:
    st.title("File Converter & Cleaner")
    st.write("Upload csv or excel files, clean data and convert formats.")
    files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)



if files:
    with tab2:
        for file in files:  # ➡️ Yeh loop files list me se ek ek karke file ko open karta hai.       
            ext = file.name.split(".")[-1]  #  Yeh file ka extension (CSV ya XLSX) nikalta hai.
            if ext == "csv":
                df = pd.read_csv(file)
            else:
                try:
                    import openpyxl
                    df = pd.read_excel(file)
                except ImportError:
                    st.error("The 'openpyxl' library is required to read Excel files. Please install it using 'pip install openpyxl'.")
                    continue


            st.subheader(f"{file.name} - Preview")  # ➡️ Yeh file ka naam dikhata hai taake user ko pata chale kaunsi file upload hui hai.

            st.dataframe(df.head())   # ➡️ Yeh file ka pehla thoda sa data dikhata hai.

            # Display duplicated lines initially

            st.subheader(f"{file.name} - Duplicated Lines")

            st.dataframe(df[df.duplicated()])


            # ➡️ Agar user checkbox pe click karega, to duplicate rows delete ho jayengi.

            if st.checkbox(f"Remove Duplicates - {file.name}"): 

                df = df.drop_duplicates()  # Yeh data se repeated rows hata dega.

                st.success("Duplicates Removed") # Ek message dikhayega ke duplicates delete ho gaye hain.

                st.dataframe(df.head())  # Naya cleaned data show karega.


            # ➡️ Agar kisi column me missing (NaN) values hain, to yeh unko fill karega.

            if st.checkbox(f"Fill Missing Values - {file.name}"):  

                missing_values = df.isnull().sum().sum()

                if missing_values > 0:
                    st.warning(f"There are {missing_values} missing values. Please fill them.")
                    st.dataframe(df.style.highlight_null(color='red'))
                    
                    # Option to fill missing values manually
                    for col in df.columns:
                        if df[col].isnull().any():
                            fill_value = st.text_input(f"Fill missing values in column '{col}' with:", key=f"{file.name}_{col}")
                            if fill_value:
                                df[col].fillna(fill_value, inplace=True)
                                st.success(f"Filled missing values in column '{col}' with '{fill_value}'")
                                st.dataframe(df.head())
                else:
                    df.fillna(df.select_dtypes(include=['number']).mean(), inplace=True)
                    st.success("Missing Values Filled with mean")
                    st.dataframe(df.head())



            # ➡️ User ko ek option milta hai ke kaunse columns rakhne hain.
            if not df.empty:
                selected_columns = st.multiselect(f"Select Columns - {file.name}", df.columns, default=df.columns)    # ✔ st.multiselect() → Yeh dropdown menu banata hai jisme columns select kar sakte hain.
                df = df[selected_columns]   # Sirf selected columns ko data me rakhta hai.
                st.dataframe(df.head())     # Naya filtered data dikhata hai.




            # ➡️ Agar user checkbox pe click karega, to numeric data ka graph dikhayega.
            if st.checkbox(f"Show Chart - {file.name}") and not df.select_dtypes(include=['number']).empty:    # ✔ st.bar_chart() → Bar chart banata hai jo sirf numeric values show karega.
                st.bar_chart(df.select_dtypes(include=['number']).iloc[:, :2])    # ✔ iloc[:, :2] → Sirf pehle 2 numeric columns ka graph banayega.



            # ➡️ User ko option milega ke file ko CSV ya Excel format me convert kare..
            format_choices = st.radio(f"Convert {file.name} to", ["CSV", "Excel"], key=file.name)



            # 🟡 **Download button ka error solve kiya**
            if st.button(f"Download {file.name} as {format_choices}"):  
                output = BytesIO()
                if format_choices == "CSV":
                    df.to_csv(output, index=False)
                    mime = "text/csv"
                    new_name = file.name.rsplit(".", 1)[0] + ".csv"
                else:
                    df.to_excel(output, index=False, engine="openpyxl")  
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    new_name = file.name.rsplit(".", 1)[0] + ".xlsx"

                output.seek(0)
                st.download_button(label=f"Download {new_name}", data=output, file_name=new_name, mime=mime)
                st.success("Processing Complete!")