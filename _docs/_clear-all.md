extra-keys = [ \
  [{macro: "clear && printf '\\e[3J'\\n", display: 'CLS'}] \
]



clear && printf '\e[3J'




bind -n C-k send-keys "clear && printf '\e[3J'" \; send-keys "Enter"