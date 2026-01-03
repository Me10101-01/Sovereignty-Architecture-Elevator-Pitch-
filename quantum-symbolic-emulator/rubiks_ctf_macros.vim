" Rubik's CTF Vim Macros - Operator Notation Instantiated
" INV-093: HYBRID - Transform operators as Vim macros
" Each macro = operator in the transform pipeline
" Rubik's faces = transformation stages

" ============================================================================
" INSTALLATION
" ============================================================================
" Add to your ~/.vimrc or source this file:
"   source /path/to/rubiks_ctf_macros.vim
"
" Or run manually in Vim:
"   :source rubiks_ctf_macros.vim

" ============================================================================
" MACROS
" ============================================================================

" @d - DNA Transcribe
" Transforms SAGCO characters to DNA sequences
" S→AGC, A→GCT, G→GGA, C→TGC, O→TAA
function! DNATranscribe()
    " Save current line
    let l:line = getline('.')
    
    " Transform SAGCO to DNA
    let l:line = substitute(l:line, 'S', 'AGC', 'g')
    let l:line = substitute(l:line, 'A', 'GCT', 'g')
    let l:line = substitute(l:line, 'G', 'GGA', 'g')
    let l:line = substitute(l:line, 'C', 'TGC', 'g')
    let l:line = substitute(l:line, 'O', 'TAA', 'g')
    
    " Replace line
    call setline('.', l:line)
    echo "DNA transcribed"
endfunction

" @h - Hex Convert
" Converts text to hexadecimal representation
function! HexConvert()
    " Save current line
    let l:line = getline('.')
    
    " Convert each character to hex
    let l:hex_output = ''
    for l:char in split(l:line, '\zs')
        let l:hex_output .= printf('%02X ', char2nr(l:char))
    endfor
    
    " Replace line with hex
    call setline('.', trim(l:hex_output))
    echo "Hex converted"
endfunction

" @b - Binary Convert
" Converts hex string to binary representation
function! BinaryConvert()
    " Save current line
    let l:line = getline('.')
    
    " Split by spaces to get hex bytes
    let l:hex_bytes = split(l:line)
    let l:binary_output = ''
    
    for l:hex_byte in l:hex_bytes
        " Convert hex to decimal then to binary
        let l:decimal = str2nr(l:hex_byte, 16)
        let l:binary = ''
        
        " Convert to 8-bit binary
        for l:i in range(7, 0, -1)
            if l:decimal >= float2nr(pow(2, l:i))
                let l:binary .= '1'
                let l:decimal -= float2nr(pow(2, l:i))
            else
                let l:binary .= '0'
            endif
        endfor
        
        let l:binary_output .= l:binary . ' '
    endfor
    
    " Replace line with binary
    call setline('.', trim(l:binary_output))
    echo "Binary converted"
endfunction

" @n - MRVE Seal (NFT Hash)
" Generates NFT-style hash using available hashing
function! MRVESeal()
    " Save current line
    let l:line = getline('.')
    
    " Use sha256 if available, otherwise simple hash
    if executable('sha256sum')
        let l:hash = system('echo -n "' . l:line . '" | sha256sum | cut -d" " -f1')
    elseif executable('shasum')
        let l:hash = system('echo -n "' . l:line . '" | shasum -a 256 | cut -d" " -f1')
    else
        " Fallback: simple hash function
        let l:hash_value = 0
        for l:char in split(l:line, '\zs')
            let l:hash_value = (l:hash_value * 31 + char2nr(l:char)) % 1000000007
        endfor
        let l:hash = printf('%08x', l:hash_value)
    endif
    
    " Append hash on next line
    call append('.', 'NFT Hash: ' . trim(l:hash))
    echo "MRVE sealed"
endfunction

" @c - Full Chain
" Execute full transformation chain: d→h→b→n
function! FullChain()
    echo "Executing full chain..."
    
    " Store original line for reference
    let l:original = getline('.')
    call append('.', 'Original: ' . l:original)
    
    " DNA transcribe
    call cursor(line('.') + 1, 0)
    call DNATranscribe()
    let l:dna = getline('.')
    call append('.', 'DNA: ' . l:dna)
    
    " Hex convert
    call cursor(line('.') + 1, 0)
    call HexConvert()
    let l:hex = getline('.')
    call append('.', 'Hex: ' . l:hex)
    
    " Binary convert
    call cursor(line('.') + 1, 0)
    call BinaryConvert()
    let l:binary = getline('.')
    call append('.', 'Binary: ' . l:binary)
    
    " MRVE seal (operates on DNA)
    call cursor(line('.') - 2, 0)  " Go back to DNA line
    call MRVESeal()
    
    echo "Full chain complete"
endfunction

" ============================================================================
" KEY MAPPINGS
" ============================================================================

" Normal mode mappings
nnoremap <Leader>d :call DNATranscribe()<CR>
nnoremap <Leader>h :call HexConvert()<CR>
nnoremap <Leader>b :call BinaryConvert()<CR>
nnoremap <Leader>n :call MRVESeal()<CR>
nnoremap <Leader>c :call FullChain()<CR>

" Visual mode mappings (operate on selection)
vnoremap <Leader>d :call DNATranscribe()<CR>
vnoremap <Leader>h :call HexConvert()<CR>
vnoremap <Leader>b :call BinaryConvert()<CR>
vnoremap <Leader>n :call MRVESeal()<CR>

" ============================================================================
" COMMANDS
" ============================================================================

command! DNATranscribe call DNATranscribe()
command! HexConvert call HexConvert()
command! BinaryConvert call BinaryConvert()
command! MRVESeal call MRVESeal()
command! FullChain call FullChain()

" ============================================================================
" HELP
" ============================================================================

function! RubiksHelp()
    echo "Rubik's CTF Vim Macros"
    echo "======================"
    echo ""
    echo "Keybindings (Normal mode):"
    echo "  <Leader>d - DNA Transcribe (SAGCO → DNA)"
    echo "  <Leader>h - Hex Convert (Text → Hex)"
    echo "  <Leader>b - Binary Convert (Hex → Binary)"
    echo "  <Leader>n - MRVE Seal (Generate NFT hash)"
    echo "  <Leader>c - Full Chain (d→h→b→n)"
    echo ""
    echo "Commands:"
    echo "  :DNATranscribe"
    echo "  :HexConvert"
    echo "  :BinaryConvert"
    echo "  :MRVESeal"
    echo "  :FullChain"
    echo ""
    echo "Example usage:"
    echo "  1. Type: SAGCO"
    echo "  2. Press: <Leader>c"
    echo "  3. View full transformation chain"
endfunction

command! RubiksHelp call RubiksHelp()

" ============================================================================
" INITIALIZATION
" ============================================================================

echo "Rubik's CTF Vim Macros loaded. Type :RubiksHelp for usage."
