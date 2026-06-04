" SAGCO VIM INTEGRATION
" Source this in ~/.vimrc:  source /path/to/repo/sagco.vim
" or add to init.vim:       source /path/to/repo/sagco.vim

let g:sagco_root = expand('<sfile>:p:h')

" ── Commands ──────────────────────────────────────────────────────────────────
command! SagcoDemo      execute '!' . g:sagco_root . '/bin/sagco demo'
command! SagcoMission   execute '!' . g:sagco_root . '/bin/sagco mission'
command! SagcoRegress   execute '!' . g:sagco_root . '/bin/sagco regression'
command! SagcoPalace    execute '!' . g:sagco_root . '/bin/sagco palace'
command! SagcoPortfolio execute '!' . g:sagco_root . '/bin/sagco portfolio'
command! SagcoList      execute '!' . g:sagco_root . '/bin/sagco list'
command! -nargs=1 SagcoNew execute '!' . g:sagco_root . '/bin/sagco new <args>'
command! -nargs=+ SagcoRun execute '!' . g:sagco_root . '/bin/sagco <args>'

" ── Leader mappings (\key in normal mode) ─────────────────────────────────────
nnoremap <leader>sd :SagcoDemo<CR>
nnoremap <leader>sm :SagcoMission<CR>
nnoremap <leader>sr :SagcoRegress<CR>
nnoremap <leader>sp :SagcoPalace<CR>
nnoremap <leader>sf :SagcoPortfolio<CR>
nnoremap <leader>sl :SagcoList<CR>

" ── Autocmd: transpile .sagco files on save ───────────────────────────────────
augroup sagco
    autocmd!
    autocmd BufWritePost *.sagco execute '!' . g:sagco_root . '/bin/sagco demo'
    autocmd BufWritePost *.flame  echom 'FlameLang updated'
augroup END

" ── Syntax hint for .sagco files ─────────────────────────────────────────────
autocmd BufRead,BufNewFile *.sagco set filetype=sh
autocmd BufRead,BufNewFile *.flame set filetype=sh
