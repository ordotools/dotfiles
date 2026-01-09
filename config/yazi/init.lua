local previewers = require("yazi.previewers")

previewers.mime.add("application/pdf", function(previewer, ctx)
  return previewer:job({
    "pdftoppm", "-png", "-singlefile", "-scale-to", "1200", ctx.file, "/tmp/yazi-pdf-thumb",
  }):then_call(function() return "/tmp/yazi-pdf-thumb.png" end)
end)
