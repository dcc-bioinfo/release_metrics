library(gplots)

message("Choose file for heatmap (tab delimited)")
raw <- read.csv(file.choose(),sep="\t")

rnames = raw[,1]


numraw = raw[-1]
# cuts out the project id and the description
numraw = numraw[-1]
numraw = numraw[-1]

mata = data.matrix(numraw)

rownames(mata) = countries


other_palette <- colorRampPalette (c("red2","yellow2","green2"))(n=100)

heatmap.2 (mata,Rowv=NA,dendrogram="none",Colv=NA,scale="none",margins=c(22,8),col=other_palette,cexRow=0.5,density.info="none",trace="none",lhei=c(0.1,0.5),hclustfun=myclust,distfun=dist,labRow=rnames,
    RowSideColors = c(
        rep("tan",4),
        rep("yellowgreen",1),
        rep("green",2),
        rep("salmon",6),
        rep("blue",1),
        rep("rosybrown",1),
        rep("palegreen",4),
        rep("brown4",3),
        rep("blueviolet",1),
        rep("coral",1),
        rep("slategray3",2),
        rep("gold",1),
        rep("steelblue",1),
        rep("darkred",2),
        rep("pink",1),
        rep("cyan3",5),
        rep("aquamarine",24),
        rep("red",5)),

)
 par(lend=1)
    legend("bottomleft",
    legend = c("AU","BR","CA","CN","EU/FR","EU","FR","GE","IN","IT","JP","SA","SG","KR","SP","TAR-US","TCGA","UK"),
        col = c("tan","yellowgreen","green","salmon","blue","rosybrown","palegreen","brown4","blueviolet","coral","slategray3","gold","steelblue","darkred","pink","cyan3","aquamarine","red"),
        lty=1,
        lwd=10,
        x.intersp = 0.03,
        y.intersp = 0.7,
        xjust = 1,
        seg.len=0.6,
        inset = -0.02,
        bty = "n"
        )

