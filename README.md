# RobotfMRI
Scripts utilized for the RobotfMRI Project

## Usage
Takes TextGrid-formatted transcriptions from the 'Multimodal corpus of bidirectional conversation of human-human and human-robot interaction during fMRI scanning' (Rauchbauer et al., 2020) as input. Returns a folder with onset and duration files that can be utilized in fMRI analysis in SPM12.

To run the program, type the following command in the terminal:
```python3 main.py [PathToTextGridFiles]```

## Required packages
```textgrid ```
```os```
```operator```
```cmath```
```glob```
```csv```
```scipy```
```sys```



## References
Rauchbauer, B., Hmamouche, Y., Bigi, B., Prevot, L., Ochs, M., & Thierry, C. (2020, November). Multimodal corpus of bidirectional conversation of human-human and human-robot interaction during fMRI scanning. In Proceedings of The 12th Language Resources and Evaluation Conference (pp. 661-668). European Language Resources Association.