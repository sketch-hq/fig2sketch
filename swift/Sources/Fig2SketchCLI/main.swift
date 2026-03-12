import Fig2SketchCore
import Foundation

var streams = StandardStreams()
let parser = CLIParser(versionString: Version.current)

do {
    switch try parser.parse(CommandLine.arguments.dropFirst()) {
    case .help(let text):
        streams.writeOut(text + "\n")
        Foundation.exit(EX_OK)
    case .version(let text):
        streams.writeOut(text + "\n")
        Foundation.exit(EX_OK)
    case .run(let options):
        Foundation.exit(CLIConversionRunner.run(options: options, output: &streams))
    }
} catch let error as CLIParseError {
    streams.writeErr(CLIParser.usageText() + "\n")
    streams.writeErr("fig2sketch: error: \(error)\n")
    Foundation.exit(2)
} catch {
    streams.writeErr("fig2sketch: error: \(error)\n")
    Foundation.exit(EX_SOFTWARE)
}
