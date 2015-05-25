msg <- "meowmeowmeow"
library(gplots)

message("Choose file for heatmap (tab delimited)")
raw <- read.csv(file.choose(),sep="\t")

rnames = raw[,1]
numraw = raw[-1]

mata = data.matrix(numraw)

rownames(mata) = rnames

other_palette <- colorRampPalette (c("red2","yellow2","green2"))(n=100)
heatmap.2 (mata,Rowv=NA,Colv=NA,scale="none",margins=c(18,6),col=other_palette,cexRow=0.5,density.info="none",trace="none")
