08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

~~MCP Registry~~ / Markitdown 

| | | an 

## Markitdown 

By ~~microsoft~~ - ¥¥ 147387 

Convert various file formats (PDF, Word, Excel, images, audio) to Markdown. 

## MarkltDown 

## (J Important 

MarkltDown performs I/O with the privileges of the current process. Like open() or requests.get(), it will access resources that the process itself can access. Sanitize your inputs in untrusted environments, and call the narrowest convert ~~_*~~ function needed for your use case (e.g., convert ~~_s~~ tream() , Of convert ~~_l~~ ocal() ). See the ~~Security~~ Considerations section of the documentation for more information. 

MarkltDown is a lightweight Python utility for converting various files to Markdown for use with LLMs and related text analysis pipelines. To this end, it is most comparable to ~~textract,~~ but with a focus on preserving important document structure and content as Markdown (including: headings, lists, tables, links, etc.) While the output is often reasonably presentable and human- ~~fr~~ iendly, it is meant to be consumed by text analysis tools -- and may not be the best option for high ~~-f~~ idelity document conversions for human consumption. 

MarkltDown currently supports the conversion from: 

- ° PDF 

- e PowerPoint 

- e Word 

- e Excel 

- e Images (EXIF metadata and OCR) 

- e Audio (EXIF metadata and speech transcription) 

https://github.com/mcp/microsoft/markitdown 

1/10 

08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

e HTML 

- e Tex ~~t-~~ based formats (CSV, JSON, XML) 

- e ZIP files (iterates over contents) 

- e Youtube URLs 

- e EPubs 

e ...and more! 

## Why Markdown? 

Markdown is extremely close to plain text, with minimal markup or formatting, but still provides a way to represent important document structure. Mainstream LLMs, such as OpenAl's GPT ~~-4~~ 0, natively "speak" Markdown, and often incorporate Markdown into their responses unprompted. This suggests that they have been trained on vast amounts of Markdown- ~~f~~ ormatted text, and understand it well. As a side benefit, Markdown conventions are also highly token- ~~e~~ fficient. 

## Prerequisites 

MarkltDown requires Python 3.10 or higher. It is recommended to use a virtual environment to avoid dependency conflicts. 

With the standard Python installation, you can create and activate a virtual environment using the following commands: 

python ~~-~~ m venv .venv (0) source .venv/bin/activate If using uv , you can create a virtual environment with: uv venv --python=3.12 .venv (0 source .venv/bin/activate # NOTE: Be sure to use ‘uv pip install’ rather than just "pip install’ to instal ee > If you are using Anaconda, you can create a virtual environment with: conda create ~~-~~ n markitdown python=3.12 O conda activate markitdown 

If using uv , you can create a virtual environment with: 

https://github.com/mcp/microsoft/markitdown 

2/10 

08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

## Installation 

To install MarkltDown, use pip: pip install 'markitdown[all]' . Alternatively, you can install it from the source: 

git clone git@github.com:microsoft/markitdown.git cd markitdown pip install ~~-~~ e ‘packages/markitdown[al1]' 

0 

## Usage 

## Command- ~~L~~ ine 

markitdown path ~~-~~ to ~~-~~ file.pdf > document.md 

(0) 

Or use ~~-~~ o to specify the output file: 

markitdown path ~~-~~ to ~~-~~ file.pdf ~~-~~ o document.md 

You can also pipe content: 

cat path ~~-~~ to ~~-~~ file.pdf | markitdown 

(0 0) 

## Optional Dependencies 

MarkltDown has optional dependencies for activating various file formats. Earlier in this document, we installed all optional dependencies with the [all] option. However, you can also install them individually for more control. For example: 

pip install ‘markitdown[pdf, docx, pptx]' 

(0) 

## will install only the dependencies for PDF, DOCX, and PPTX files. 

At the moment, the following optional dependencies are available: 

- e [all] Installs all optional dependencies 

- © [pptx] Installs dependencies for PowerPoint files 

- © [docx] Installs dependencies for Word files 

- e® [xlsx] Installs dependencies for Excel files e [xls] Installs dependencies for older Excel files 

https://github.com/mcp/microsoft/markitdown 

3/10 

08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

- e [pdf] Installs dependencies for PDF files 

- e [outlook] Installs dependencies for Outlook messages 

- e [az ~~-~~ doc ~~-~~ intel] Installs dependencies for Azure Document Intelligence 

- e [az ~~-~~ content ~~-~~ understanding] Installs dependencies for Azure Content Understanding e [audio ~~-~~ transcription] Installs dependencies for audio transcription of wav and mp3 files 

- e [youtube ~~-~~ transcription] Installs dependencies for fetching YouTube video transcription 

## Plugins 

MarkltDown also supports 3rd ~~-~~ party plugins. Plugins are disabled by default. To list installed plugins: 

markitdown --list ~~-~~ plugins 

(O 

To enable plugins use: 

markitdown --use ~~-~~ plugins pat ~~h~~ - ~~to~~ -file.pdf 

(O 

To find available plugins, search GitHub for the hashtag #markitdown ~~-~~ plugin . To develop a plugin, see packages/markitdown ~~-~~ sample ~~-~~ plugin . 

## markitdown ~~-o~~ cr Plugin 

The markitdown ~~-~~ ocr plugin adds OCR support to PDF, DOCX, PPTX, and XLSX converters, extracting text from embedded images using LLM Vision ~~—~~ the same 11m ~~c~~ lient / 11 ~~m_~~ model pattern that MarkltDown already uses for image descriptions. No new ML libraries or binary dependencies required. 

Installation: 

pip install markitdown ~~-~~ ocr pip install openai # or any OpenAI ~~-~~ compatible client 

(0 

## Usage: 

Pass the same 1l ~~m_~~ client and 11 ~~m_m~~ odel you would use for image descriptions: 

from markitdown import MarkItDown from openai import OpenAI 

**==> picture [13 x 15] intentionally omitted <==**

**----- Start of picture text -----**<br>
O<br>**----- End of picture text -----**<br>


md = MarkItDown( 

https://github.com/mcp/microsoft/markitdown 

4/10 

08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

enable ~~_p~~ lugins=True, 

ll ~~m_~~ client=OpenAI(), 

llm ~~_m~~ odel="gpt- ~~4~~ o0", 

) result = md.convert("document ~~_w~~ ith ~~_i~~ mages. pdf") print(result.text ~~_c~~ ontent) 

If nO 11 ~~m_~~ client is provided the plugin still loads, but OCR is silently skipped and the standard built ~~-~~ in converter is used instead. 

See ~~packages/markitdown-ocr/README.md~~ for detailed documentation. 

## Azure Content Understanding 

~~Azure Content Understanding~~ provides higher ~~-q~~ uality conversion with structured field extraction (YAML front matter), mult ~~i-~~ modal support (documents, images, audio, video), and configurable analyzers. 

Install: pip install ‘markitdown[az ~~-~~ content ~~-~~ understanding] ' 

## When to use Content Understanding 

Content Understanding is ideal when you need capabilities beyond what built ~~-~~ in or Document Intelligence converters provide: 

- e Audio and video files ~~—~~ CU is the only option for video, and the higher ~~-q~~ uality cloud option for audio. Built ~~-~~ in converters have no video support and only basic audio transcription. 

- e Structured field extraction ~~— Prebuilt~~ or ~~custom-built~~ analyzers extract domain- ~~s~~ pecific fields (invoice amounts, receipt dates, contract clauses) serialized as YAML front matter. Neither built ~~-~~ in nor Doc Intel integration exposes fields. 

- e Higher ~~-q~~ uality document extraction ~~—~~ Cloud ~~-~~ based layout analysis and OCR for scanned PDFs, complex tables, and mult ~~i-~~ page documents. 

- e Single API for all modalities ~~—~~ One c ~~u_~~ endpoint handles documents, images, audio, and video with automatic analyzer routing. 

**==> picture [470 x 124] intentionally omitted <==**

**----- Start of picture text -----**<br>
|||||||||
|---|---|---|---|---|---|---|---|
|-|Built|-|in|Azure|Document|Azure|Content|
|Capability|.|.|
|converters|Intelligence|Understanding|
|Document|Offline,|format|-|Cloud|layout|Cloud|multimodal|
|conversion|specific|extraction|extraction|extraction|
|Structured|Not|exposed|by|this|= YAML|front|matter from|
|fields|Not|available|integration|analyzer fields|

**----- End of picture text -----**<br>


https://github.com/mcp/microsoft/markitdown 

5/10 

08/06/2026 03:22 

|_<br>Capability|Built~~-~~in<br>converters|Azure Document<br>.<br>Intelligence|Azure Content<br>.<br>Understanding|
|---|---|---|---|
|Custom<br>analyzers|Notavailable|Not configurable in<br>,<br>this integration|Supported with<br>c~~u_~~analyzer~~_i~~d|
|Audio and<br>video|Basic audio, no<br>video|Notsupported|Audio and video<br>analyzers|
|Cost|Local compute<br>only|BillableAzureAPI<br>calls|.<br>BillableAzureAPI calls|



CLI: 

markitdown path ~~-~~ to ~~-~~ file.pdf --use ~~-~~ cu --cu ~~-~~ endpoint "<conte ~~n~~ t_understa ~~nde~~ ndpcing (0) ~~ee~~ > 

## Python API: 

## from markitdown import MarkItDown 

(0) 

# Zero ~~-~~ config ~~—~~ auto ~~-~~ selects analyzer per file type md = MarkItDown ~~(c~~ u_endpoint="< ~~co~~ ntent_und ~~ere~~ standingndpoint>") result = md.convert("report.pdf") # documents > prebuilt ~~-~~ documentSearch result = md.convert("meeting.mp4") # video > prebuilt ~~-~~ videoSearch result = md.convert("call.wav") # audio > prebuilt ~~-~~ audioSearch print(result.markdown) 

## With a custom analyzer (for domain- ~~s~~ pecific field extraction): 

md = MarkItDown( 

(0) 

c ~~u_~~ endpoint="<c ~~on~~ tent_unde ~~rse~~ ndpoint>",tanding c ~~u_~~ analyzer ~~_i~~ d="my ~~-~~ invoice ~~-a~~ nalyzer", 

) result = md.convert("invoice.pdf") print(result.markdown) 

# Output includes YAML front matter with extracted fields: # --- 

# contentType: document 

# fields: # = VendorName: CONTOSO LTD. # InvoiceDate: '2019 ~~-~~ 11 ~~-1~~ 5' # --# <!-page 1 --> 

https://github.com/mcp/microsoft/markitdown 

6/10 

08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

When c ~~u_~~ analyzer ~~_i~~ d is set, the converter automatically scopes it to compatible file types based on the analyzer's modality. Incompatible types (e.g., audio files with a document analyzer) auto ~~-~~ route to default prebuilt analyzers. 

Cost note: Each convert() call for a CU ~~-r~~ outed format is a billable Azure API call. Use c ~~u_~~ file ~~_t~~ ypes to restrict which formats route to CU: 

from markitdown.converters import ContentUnderstandingFileType 

(Oo 

md = MarkItDown( c ~~u_~~ endpoint="<c ~~on~~ tent_unde ~~rse~~ ndpoint>",tanding c ~~u_~~ fil ~~e_t~~ ypes=[ContentUnderstandingFileType.PDF], # only PDFs use CU 

) 

More information about Azure Content Understanding can be found ~~here.~~ 

## Azure Document Intelligence 

To use Microsoft Document Intelligence for conversion: 

markitdown path ~~-~~ to ~~-~~ file.pdf ~~-~~ o document.md ~~-~~ d ~~-~~ e "<document ~~_i~~ ntelligence ~~_e~~ ndpoir (0 

~~eee~~ > 

More information about how to set up an Azure Document Intelligence Resource can be found here 

## Python API 

Basic usage in Python: 

## from markitdown import MarkItDown 

(O) 

md = MarkItDown(enable ~~p~~ lugins=False) # Set to True to enable plugins result = md.convert("test.xlsx") print(result.text ~~_c~~ ontent) 

## Document Intelligence conversion in Python: 

## from markitdown import MarkItDown 

(0) 

md = MarkItDown(docintel ~~_e~~ ndpoint="<document ~~_i~~ ntelligence ~~_e~~ ndpoint>") result = md.convert("test.pdf") print(result.text ~~_c~~ ontent) 

https://github.com/mcp/microsoft/markitdown 

7/10 

08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

To use Large Language Models for image descriptions (currently only for pptx and image files), provide 11 ~~m_~~ client and 11 ~~m_m~~ odel : 

## from markitdown import MarkItDown 

(0) 

from openai import OpenAI 

client = OpenAI() md = MarkItDown(1ll ~~m_~~ client=client, 1l ~~m_~~ model="gpt ~~-4~~ 0", 1ll ~~m_~~ prompt="optional cust result = md.convert("example.jpg") print(result.text ~~_c~~ ontent) 

## ee—CSSCSCCié‘( 

> 

## Docker 

docker build ~~-~~ t markitdown:latest . docker run --rm ~~-~~ i markitdown:latest < ~/your ~~-~~ file.pdf > output.md 

O 

## Contributing 

This project welcomes contributions and suggestions. Most contributions require you to agree toa 

Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us 

the rights to use your contribution. For details, visit ~~https://cla.opensource.microsoft.com.~~ 

When you submit a pull request, a CLA bot will automatically determine whether you need to provide 

a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions 

provided by the bot. You will only need to do this once across all repos using our CLA. 

This project has adopted the ~~Microsoft Open Source Code of Conduct.~~ 

For more information see the Code of Conduct FAQ or 

contact ~~opencode@microsoft.com~~ with any additional questions or comments. 

## How to Contribute 

You can help by looking at issues or helping review PRs. Any issue or PR is welcome, but we have also marked some as ‘open for contribution’ and ‘open for reviewing’ to help facilitate community contributions. These are of course just suggestions and you are welcome to contribute in any way you like. 

https://github.com/mcp/microsoft/markitdown 

8/10 

08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

|||||All||Especially Needs Help from Community|Especially Needs Help from Community|Especially Needs Help from Community|Especially Needs Help from Community|
|---|---|---|---|---|---|---|---|---|---|
|Issues||~~Allissues~~|||— ~~Issues ~~||~~open for contribution~~|||
|PRs||~~AllPRs~~||||~~PRsopenforreviewing~~||||



## Running Tests and Checks 

e Navigate to the MarkltDown package: 

cd packages/markitdown (0 Install hatch in your environment and run tests: pip install hatch # Other ways of installing hatch: https://hatch.pypa.io/: (O hatch shell hatch test ~~i~~ eeeererr—SCSSCC‘N > (Alternative) Use the Devcontainer which has all the dependencies installed: # Reopen the project in Devcontainer and run: () 

e Install hatch in your environment and run tests: 

# Reopen the project in Devcontainer and run: hatch test 

e Run pr ~~e-~~ commit checks before submitting a PR: pre ~~-~~ commit run --all ~~-~~ files 

## Security Considerations 

MarkltDown performs I/O with the privileges of the current process. Like open() or requests.get() , it will access resources that the process itself can access. 

Sanitize your inputs: Do not pass untrusted input directly to MarkltDown. If any part of the input may be controlled by an untrusted user or system, such as in hosted or server ~~-~~ side applications, it must be validated and restricted before calling MarkltDown. Depending on your environment, this may include restricting file paths, limiting URI schemes and network destinations, and blocking access to private, loopback, link-local, or metadata ~~-s~~ ervice addresses. 

https://github.com/mcp/microsoft/markitdown 

9/10 

08/06/2026 03:22 

MCP Registry | Markitdown - GitHub 

Call only the conversion method you need: Prefer the narrowest conversion API that fits your use case. MarkltDown's convert() method is intentionally permissive and can handle local files, remote URIs, and byte streams. If your application only needs to read local files, call convert ~~_l~~ ocal() instead. If you need more control over URI fetching, call requests.get() yourself and pass the response object to convert ~~_r~~ esponse() . For maximum control, open a stream to the input you want converted and call convert ~~_s~~ tream() . 

## Contributing 3rd ~~-~~ party Plugins 

You can also contribute by creating and sharing 3rd party plugins. See packages/markitdown ~~-~~ sample ~~-~~ plugin for more details. 

## Trademarks 

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 

trademarks or logos is subject to and must follow 

Microsoft's Trademark & Brand Guidelines. 

Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. 

Any use of third ~~-~~ party trademarks or logos are subject to those third ~~-~~ party’s policies. 

## Resources 

fF] microsoft/ markitdown 

Q) Contact support 

https://github.com/mcp/microsoft/markitdown 

10/10 

