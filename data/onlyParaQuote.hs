-- onlyParaOrQuote.hs
import Text.Pandoc
import Text.Pandoc.Walk (walk)

filtr :: Block -> Block
filtr v@(Para _) = v
filtr v@(BlockQuote _) = v
filtr _ = Null

readDoc :: String -> Pandoc
readDoc s = case readMarkdown def s of
                 Right doc -> doc
                 Left err  -> error (show err)

writeDoc :: Pandoc -> String
writeDoc doc = writeMarkdown def doc

main :: IO ()
main = interact (writeDoc . walk filtr . readDoc)
