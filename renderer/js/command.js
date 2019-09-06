class Command
{
    constructor(cmdFunction, args)
    {
        this.cmdFunction = cmdFunction;
        this.args        = args;
    }

    Execute()
    {
        this.cmdFunction(this.args);
    }
}