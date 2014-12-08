" -k
set nocompatible
filetype plugin indent on
syntax on
nnoremap <Leader>s :set syntax=
nnoremap <Leader>S :set filetype=
set nomodeline
set hidden

" save everything: registers, marks, command line & search...
set history=1000000
set viminfo='100000,h
set sessionoptions=tabpages,blank,help,buffers,folds,localoptions,slash,unix,winsize
nmap SQ <ESC>:mksession! ~/.vim/Session.vim<CR>:wqa<CR> 
fu! RestoreSession()
    if argc() == 0 "vim called without arguments
        execute 'source ~/.vim/Session.vim'
    end
endfunction

autocmd VimEnter * call RestoreSession()
nmap SS :wa<CR>:mksession! ~/sessions/
nmap SO :wa<CR>:so ~/sessions/

set tabpagemax=50
set switchbuf=useopen,usetab

set hlsearch
set ignorecase
set smartcase
" set incsearch

set backspace=indent,eol
set autoindent
set startofline
set nopaste
set pastetoggle=<f11>

set wildchar=<Tab>
" set wildmenu
set wildmode=longest,list,full
set noignorecase
set complete=.,i,t
set completeopt=menu,menuone,longest " ???
" set completeopt=longest " ???

set showcmd
set laststatus=2
set cmdheight=1
set statusline=%f%m%r%h%w\ [%n:%{&ff}/%Y]%=[0x\%04.4B][%03v][%p%%\ line\ %l\ of\ %L]

set number
set visualbell
set t_vb=
set notimeout ttimeout ttimeoutlen=200

set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab
set ignorecase
set smartcase

nnoremap <F1> :help <C-R><C-W><CR> " help the word under cursor
" Todo: Make a similar visual-mode binding; allow customization of the width.
nnoremap Q gqap " reformat current paragraph
nnoremap <C-L> :nohl<CR><C-L> " drop search highlighting
nnoremap <C-Bslash>       :set hls!<bar>:set hls?<CR> " switch search highlighting
inoremap <C-Bslash>       <Esc>:set hls!<bar>:set hls?<CR>a

nnoremap <Leader>t :tabnew 
nmap <Leader>T :tabnew<CR><Leader>v<CR>
" the preceding mapping is specifically made to refer to the following one.
nnoremap <Leader>v :vsplit 
" buffer superhuman - fly rather than walk VIMGOR YEAH
nnoremap <Leader>b :buffers<CR>
nnoremap <Leader>l :ls<CR>:b<SPACE>
nnoremap <Leader>d :ls<CR>:bd<SPACE>
nnoremap <Leader>B :buffers!<CR>
nnoremap <Leader>L :ls!<CR>:b<SPACE>
nnoremap <Leader>D :ls!<CR>:bd<SPACE>
" We may also like to make a function able to :bdelete all buffers matching a
" glob; the means for doing so are proposed in the relevant irclog from 02/iv-13, please refer.

" self-destructing help letter, a grace de monsieur Accolade.
nnoremap <Leader>h :cmap <lt>CR> <lt>CR><lt>C-w>o:cunmap <lt>lt>CR><lt>CR><CR>:h<space>

nnoremap <Leader>V :display<CR>
nnoremap <Leader>M :marks<CR>

" :bro ol could give you very many options, so this is a bind to filter a part
" of them containing a regex.
" nnoremap <Leader>f :call BroOlFilter()

" function BroOlFilter()
"     "the idea is to temporarily filter v:oldfiles
"     ask for a regex
"     for each in v:oldfiles
"         if line matches regex
"             add line to lines
"         end
"         if length(lines)
"             exchange lines v:oldfiles
"             bind self-destructing expression for exchange on enter key
"             :bro ol
"         end
"     end
" endfunction 

nnoremap <Leader>w :set invwrap<CR> " set/unset wrapping long lines.
" <C-^> only gets one element back in buffer history; we may try to make it
" accept argument not as a buffer number, but as a nth-recently-used buffer value. 

nnoremap <Leader>fi :set foldmethod=indent<CR>
nnoremap <Leader>fm :set foldmethod=manual<CR>
nnoremap <Leader>fe :set foldmethod=expr<CR>
nnoremap <Leader>fs :set foldmethod=syntax<CR>

let g:EasyMotion_leader_key="<space>"
let g:zenburn_high_Contrast=1
colors zenburn
hi   Normal             ctermbg=016   ctermfg=249
hi   Comment            ctermbg=016   ctermfg=060
hi   Statement          ctermbg=016   ctermfg=173
hi   String             ctermbg=016   ctermfg=067
hi   MatchParen         ctermbg=016   ctermfg=118
hi   Error              ctermbg=016   ctermfg=202
hi   Visual             ctermbg=249   ctermfg=016
hi   EasyMotionTarget   ctermfg=046


fu! RegisterTabularize()
    if exists(":Tabularize")
        nmap <Leader>a= :Tabularize /
        vmap <Leader>a= :Tabularize /
    endif
endfunction

fu! RegisterSyntastic()
    if exists(":SyntasticInfo")
        nmap <Leader>L :SyntasticToggleMode<CR>
    endif
endfunction

execute pathogen#infect() 
autocmd VimEnter * :call RegisterTabularize()
autocmd VimEnter * :call RegisterSyntastic()


set colorcolumn=+1,+2,+3
highlight ColorColumn ctermbg=234
set textwidth=98
set formatoptions=qro

