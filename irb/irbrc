# Add color coding based on Rails environment for safety

if defined? Rails
  banner = if Rails.env.production?
    "\e[41;97;1m #{Rails.env} \e[0m "
  else
    "\e[42;97;1m #{Rails.env} \e[0m "
  end


IRB.conf[:PROMPT][:MY_PROMPT] = { # name of prompt mode
  :AUTO_INDENT => true,           # enables auto-indent mode
  :PROMPT_I => "➜ ",              # simple prompt
  :PROMPT_S => '➜ ',               # prompt for continuated strings
  :PROMPT_C => '➜ ',               # prompt for continuated statement
  :RETURN   => "👉 %s\n"          # format to return value
}

  # Use custom prompt by default
  IRB.conf[:PROMPT_MODE] = :MY_PROMPT
end

